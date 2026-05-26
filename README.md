# SkyManager

![Tests](https://github.com/awuuu-tti/SkyManager/actions/workflows/test.yml/badge.svg)

![Build](https://github.com/awuuu-tti/SkyManager/actions/workflows/build.yml/badge.svg)

![Deploy](https://github.com/awuuu-tti/SkyManager/actions/workflows/deploy.yml/badge.svg)

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
- app.py — основной файл Flask-приложения
- db.py — работа с Excel-файлом
- templates — HTML-шаблоны
- static — стили сайта
- data — файл базы данных


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
## CI/CD Automation

В проекте настроена автоматизация с помощью GitHub Actions.

### Настроенные workflow

- Tests — автоматический запуск тестов pytest
- Build — автоматическая проверка сборки проекта
- Deploy — автоматический запуск deploy workflow

### Используемые технологии

- GitHub Actions
- pytest
- Python 3.11
- Ubuntu Runner