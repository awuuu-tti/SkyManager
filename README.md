# SkyManager

## Описание
Сайт разработан на Python Flask.  
Данные хранятся в Excel-файле.  
Система поддерживает роли:
- клиент
- сотрудник
- администратор

## Возможности
- регистрация и вход
- поиск рейсов
- бронирование билетов
- отмена бронирования
- управление рейсами
- изменение статуса рейса
- список пассажиров для оповещения
- отчеты по продажам
- администрирование пользователей

## Технологии
- Python
- Flask
- HTML/CSS
- Excel (openpyxl)

## Запуск
```bash
pip install -r requirements.txt
python app.py
```

Открыть в браузере:

```text
http://127.0.0.1:5000
```

## Демо-аккаунты

- admin@skymanager.local / Admin123!
- employee@skymanager.local / Employee123!
- client@skymanager.local / Client123!

## Структура проекта

```text
skymanager/
├── app.py
├── db.py
├── requirements.txt
├── README.md
├── data/
│   └── airline_data.xlsx
├── backups/
├── static/
│   └── style.css
└── templates/
    ├── admin.html
    ├── base.html
    ├── book.html
    ├── dashboard.html
    ├── employee.html
    ├── error.html
    ├── flight.html
    ├── flight_form.html
    ├── home.html
    ├── login.html
    ├── passengers.html
    ├── register.html
    ├── reports.html
    └── search.html
```
