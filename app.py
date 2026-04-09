from __future__ import annotations

import re
from functools import wraps
from flask import Flask, abort, flash, g, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from db import DISCOUNTS, LABELS, ROLES, STATUSES, add_booking, add_log, active_bookings_for_flight, backup_database, booking_by_id, bookings_for_user, cancel_booking, ensure_db, flight_by_id, next_id, read_sheet, remove_flight, remove_user, report_rows, reset_password, save_flight, save_user, user_by_email, user_by_id

app = Flask(__name__)
app.config['SECRET_KEY'] = 'student-simple-secret'
email_ok = lambda s: re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', s or '')
phone_ok = lambda s: re.fullmatch(r'[+0-9\-()\s]{8,20}', s or '')
date_ok = lambda s: re.fullmatch(r'\d{4}-\d{2}-\d{2}', s or '')
pass_ok = lambda s: len(s or '') >= 8


def current_user(): return user_by_id(session.get('user_id')) if session.get('user_id') else None

def protected(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not g.user: return redirect(url_for('login', next=request.path))
            if roles and g.user['role'] not in roles: abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.before_request
def prepare(): ensure_db(); g.user = current_user()
@app.context_processor
def inject(): return {'current_user': g.user, 'roles': ROLES, 'labels': LABELS, 'statuses': STATUSES}
@app.errorhandler(403)
def e403(_): return render_template('error.html', title='Доступ запрещен', text='У вас нет прав для этой страницы.'), 403
@app.errorhandler(404)
def e404(_): return render_template('error.html', title='Страница не найдена', text='Проверьте адрес страницы.'), 404
@app.errorhandler(500)
def e500(_): return render_template('error.html', title='Техническая ошибка', text='Попробуйте еще раз позже.'), 500


# Главная страница сайта
@app.route('/')
def home(): return render_template('home.html', flights=read_sheet('flights')[:5], cities=sorted({f['origin'] for f in read_sheet('flights')} | {f['destination'] for f in read_sheet('flights')}))

@app.route('/search')
def search():
    q = {k: (request.args.get(k) or '').strip() for k in ['origin', 'destination', 'departure_date']}
    flights = [f for f in read_sheet('flights') if (not q['origin'] or f['origin'] == q['origin']) and (not q['destination'] or f['destination'] == q['destination']) and (not q['departure_date'] or str(f['departure_date']) == q['departure_date'])]
    return render_template('search.html', flights=flights, q=q)

@app.route('/flight/<int:flight_id>')
def flight(flight_id): return render_template('flight.html', flight=flight_by_id(flight_id) or abort(404))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = {k: (request.form.get(k) or '').strip() for k in ['full_name', 'email', 'phone', 'birth_date']}; form['email'] = form['email'].lower(); pwd = request.form.get('password') or ''
        errors = [m for ok, m in [(len(form['full_name']) >= 5, 'Введите ФИО.'), (email_ok(form['email']), 'Некорректный email.'), (not user_by_email(form['email']), 'Такой email уже есть.'), (phone_ok(form['phone']), 'Некорректный телефон.'), (date_ok(form['birth_date']), 'Дата должна быть в формате ГГГГ-ММ-ДД.'), (pass_ok(pwd), 'Пароль должен быть не короче 8 символов.'), (pwd == (request.form.get('confirm_password') or ''), 'Пароли не совпадают.')] if not ok]
        if errors: [flash(e, 'danger') for e in errors]
        else:
            save_user({'id': next_id('users'), 'full_name': form['full_name'], 'email': form['email'], 'phone': form['phone'], 'birth_date': form['birth_date'], 'password_hash': generate_password_hash(pwd), 'role': 'client', 'is_active': 1, 'loyalty_member': 1 if request.form.get('loyalty_member') else 0, 'created_at': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            add_log('register', f"Новый пользователь {form['email']}")
            flash('Регистрация завершена. Теперь войдите.', 'success'); return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = user_by_email((request.form.get('email') or '').strip().lower()); pwd = request.form.get('password') or ''
        if not user or not check_password_hash(user['password_hash'], pwd): flash('Неверный email или пароль.', 'danger')
        else:
            session.clear(); session['user_id'] = int(user['id']); add_log('login', f"Вход {user['email']}", user); flash('Вход выполнен.', 'success')
            return redirect(url_for('employee' if user['role'] in ['employee', 'admin'] else 'dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); flash('Вы вышли из системы.', 'info'); return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
@protected('client', 'employee', 'admin')
def dashboard():
    if request.method == 'POST':
        form = {k: (request.form.get(k) or '').strip() for k in ['full_name', 'email', 'phone', 'birth_date']}; form['email'] = form['email'].lower()
        errors = [m for ok, m in [(len(form['full_name']) >= 5, 'Введите ФИО.'), (email_ok(form['email']), 'Некорректный email.'), (phone_ok(form['phone']), 'Некорректный телефон.'), (date_ok(form['birth_date']), 'Дата должна быть в формате ГГГГ-ММ-ДД.') ] if not ok]
        if errors: [flash(e, 'danger') for e in errors]
        else:
            user = g.user | form; save_user(user); add_log('profile', 'Профиль обновлен', g.user); flash('Профиль обновлен.', 'success')
    return render_template('dashboard.html', bookings=bookings_for_user(g.user['id']))

@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
@protected('client', 'employee', 'admin')
def book(flight_id):
    flight = flight_by_id(flight_id) or abort(404); count = max(1, min(9, int((request.values.get('count') or '1'))))
    if request.method == 'POST':
        passengers = [{'name': (request.form.get(f'name_{i}') or '').strip(), 'category': request.form.get(f'category_{i}') or 'adult'} for i in range(1, count + 1)]
        errors = ['Заполните ФИО всех пассажиров.'] if any(len(p['name']) < 5 for p in passengers) else []
        if flight['status'] == 'Отменен': errors.append('Нельзя бронировать отмененный рейс.')
        if count > int(flight['free_seats']): errors.append('На рейсе недостаточно мест.')
        if errors: [flash(e, 'danger') for e in errors]
        elif add_booking(g.user, flight, passengers): add_log('booking', f"Оформлено мест: {count} на рейс {flight['flight_number']}", g.user); flash('Бронирование создано.', 'success'); return redirect(url_for('dashboard'))
        else: flash('Места уже закончились. Обновите страницу.', 'danger')
    preview = [int(float(flight['base_price']) * (100 - DISCOUNTS[request.values.get(f'category_{i}', 'adult')]) / 100) for i in range(1, count + 1)]
    return render_template('book.html', flight=flight, count=count, preview=sum(preview))

@app.post('/booking/<int:booking_id>/cancel')
@protected('client', 'employee', 'admin')
def cancel(booking_id):
    booking = booking_by_id(booking_id) or abort(404)
    if int(booking['user_id']) != int(g.user['id']) and g.user['role'] not in ['employee', 'admin']: abort(403)
    elif booking['status'] != 'active': flash('Бронирование уже неактивно.', 'warning')
    elif int(booking['cancel_allowed'] or 0) != 1: flash('Для тарифа Promo отмена недоступна.', 'danger')
    else: cancel_booking(booking_id); add_log('cancel_booking', f"Отменено бронирование {booking['booking_code']}", g.user); flash('Бронирование отменено.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/employee')
@protected('employee', 'admin')
def employee(): return render_template('employee.html', flights=read_sheet('flights'))

@app.route('/employee/flight', methods=['GET', 'POST'])
@protected('employee', 'admin')
def employee_flight():
    flight = flight_by_id(request.args.get('id', 0)) if request.args.get('id') else None
    if request.method == 'POST':
        form = {k: (request.form.get(k) or '').strip() for k in ['flight_number', 'origin', 'destination', 'departure_date', 'departure_time', 'arrival_time', 'plane_model', 'total_seats', 'free_seats', 'base_price', 'status', 'fare_type']}
        errors = [m for ok, m in [(form['flight_number'], 'Введите номер рейса.'), (form['origin'], 'Введите город вылета.'), (form['destination'], 'Введите город прилета.'), (date_ok(form['departure_date']), 'Введите дату.'), (form['status'] in STATUSES, 'Некорректный статус.'), (form['fare_type'] in ['Promo', 'Standard', 'Flexible'], 'Некорректный тариф.')] if not ok]
        if errors: [flash(e, 'danger') for e in errors]
        else:
            row = {'id': int(request.form.get('id') or next_id('flights')), 'flight_number': form['flight_number'], 'origin': form['origin'], 'destination': form['destination'], 'departure_date': form['departure_date'], 'departure_time': form['departure_time'], 'arrival_time': form['arrival_time'], 'plane_id': 0, 'plane_model': form['plane_model'] or 'Самолет', 'total_seats': int(form['total_seats'] or 0), 'free_seats': int(form['free_seats'] or 0), 'base_price': int(form['base_price'] or 0), 'status': form['status'], 'fare_type': form['fare_type'], 'created_at': (flight or {}).get('created_at', __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
            save_flight(row); add_log('save_flight', f"Сохранен рейс {row['flight_number']}", g.user); flash('Рейс сохранен.', 'success'); return redirect(url_for('employee'))
    return render_template('flight_form.html', flight=flight)

@app.post('/employee/flight/<int:flight_id>/status')
@protected('employee', 'admin')
def change_status(flight_id): row = flight_by_id(flight_id) or abort(404); row['status'] = request.form.get('status'); save_flight(row); flash('Статус изменен.', 'success'); return redirect(url_for('employee'))

@app.post('/employee/flight/<int:flight_id>/delete')
@protected('employee', 'admin')
def delete_flight(flight_id):
    if active_bookings_for_flight(flight_id): flash('Нельзя удалить рейс с проданными билетами.', 'danger')
    else: remove_flight(flight_id); add_log('delete_flight', f'Удален рейс {flight_id}', g.user); flash('Рейс удален.', 'success')
    return redirect(url_for('employee'))

@app.route('/employee/flight/<int:flight_id>/passengers')
@protected('employee', 'admin')
def passengers(flight_id): return render_template('passengers.html', flight=flight_by_id(flight_id) or abort(404), bookings=active_bookings_for_flight(flight_id))

@app.route('/reports')
@protected('employee', 'admin')
def reports():
    rows = report_rows((request.args.get('start_date') or '').strip() or None, (request.args.get('end_date') or '').strip() or None)
    total = sum(int(r['final_price']) for r in rows); by_discount = {LABELS[k]: sum(1 for r in rows if r['passenger_category'] == k) for k in LABELS}; load = [{'flight': f, 'load': round((int(f['total_seats']) - int(f['free_seats'])) * 100 / max(1, int(f['total_seats'])), 1)} for f in read_sheet('flights')]
    return render_template('reports.html', rows=rows, total=total, by_discount=by_discount, load=load)

@app.route('/admin', methods=['GET', 'POST'])
@protected('admin')
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_staff':
            form = {k: (request.form.get(k) or '').strip() for k in ['full_name', 'email', 'phone', 'birth_date', 'role']}; pwd = request.form.get('password') or ''; form['email'] = form['email'].lower()
            errors = [m for ok, m in [(len(form['full_name']) >= 5, 'Введите ФИО.'), (email_ok(form['email']), 'Некорректный email.'), (not user_by_email(form['email']), 'Такой email уже есть.'), (phone_ok(form['phone']), 'Некорректный телефон.'), (date_ok(form['birth_date']), 'Введите дату.'), (form['role'] in ['employee', 'admin'], 'Роль должна быть employee или admin.'), (pass_ok(pwd), 'Пароль должен быть не короче 8 символов.')] if not ok]
            if errors: [flash(e, 'danger') for e in errors]
            else: save_user({'id': next_id('users'), 'full_name': form['full_name'], 'email': form['email'], 'phone': form['phone'], 'birth_date': form['birth_date'], 'password_hash': generate_password_hash(pwd), 'role': form['role'], 'is_active': 1, 'loyalty_member': 1 if form['role'] == 'employee' else 0, 'created_at': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}); flash('Сотрудник создан.', 'success')
        if action == 'delete_user': remove_user(int(request.form.get('user_id') or 0)); flash('Пользователь отключен.', 'success')
        if action == 'reset_password': reset_password(int(request.form.get('user_id') or 0), request.form.get('new_password') or 'Newpass123'); flash('Пароль обновлен.', 'success')
    return render_template('admin.html', users=[u for u in read_sheet('users') if int(u['is_active'] or 0) == 1], logs=read_sheet('logs')[-20:][::-1])

@app.route('/admin/backup')
@protected('admin')
def backup(): return send_file(backup_database(), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
