# Hop & Barley

Интернет-магазин продукции из хмеля на Django.

Проект разработан на Django и Django REST Framework и включает веб-интерфейс магазина, корзину на сессиях, оформление заказов, личный кабинет пользователя, отзывы, mock-платежи, REST API, JWT-аутентификацию, PostgreSQL, Docker Compose, автоматические тесты и CI через GitHub Actions.

---

## Содержание

* [Возможности проекта](#возможности-проекта)
* [Технологии](#технологии)
* [Структура проекта](#структура-проекта)
* [Требования](#требования)
* [Установка](#установка)
* [Настройка окружения](#настройка-окружения)
* [Запуск проекта](#запуск-проекта)
* [PostgreSQL и Docker](#postgresql-и-docker)
* [Миграции](#миграции)
* [Django Admin](#django-admin)
* [Корзина](#корзина)
* [Оформление заказа](#оформление-заказа)
* [Платежи](#платежи)
* [Пользователи и профиль](#пользователи-и-профиль)
* [Отзывы](#отзывы)
* [REST API](#rest-api)
* [JWT-аутентификация](#jwt-аутентификация)
* [OpenAPI и Swagger](#openapi-и-swagger)
* [Тестирование](#тестирование)
* [Проверка качества кода](#проверка-качества-кода)
* [CI GitHub Actions](#ci-github-actions)
* [Полезные команды](#полезные-команды)
* [Безопасность](#безопасность)
* [Статус проекта](#статус-проекта)

---

## Возможности проекта

### Интернет-магазин

Веб-часть приложения предоставляет:

* каталог товаров;
* категории товаров;
* поиск товаров;
* фильтрацию по категории;
* фильтрацию по диапазону цен;
* сортировку товаров;
* страницу товара;
* фотографии товаров;
* отображение остатка товара;
* проверку доступного количества товара;
* корзину на основе Django sessions;
* добавление товаров в корзину;
* изменение количества товаров;
* удаление товаров из корзины;
* оформление заказа;
* историю заказов;
* личный кабинет;
* регистрацию;
* авторизацию;
* выход из аккаунта;
* отзывы о товарах.

---

## Технологии

Основные технологии проекта:

* Python 3.12;
* Django 6.1.1;
* Django REST Framework;
* Simple JWT;
* drf-spectacular;
* SQLite для локальной разработки;
* PostgreSQL;
* Docker;
* Docker Compose;
* Ruff;
* mypy;
* Django Test Framework;
* GitHub Actions.

---

## Структура проекта

```text
hop_django/
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── ci.py
│   └── urls.py
│
├── products/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── serializers.py
│   ├── api_views.py
│   └── tests/
│
├── orders/
│   ├── models.py
│   ├── views.py
│   ├── cart.py
│   ├── services.py
│   ├── forms.py
│   ├── serializers.py
│   ├── api_views.py
│   └── tests/
│
├── users/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── serializers.py
│   ├── api_views.py
│   └── tests/
│
├── reviews/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── serializers.py
│   ├── api_views.py
│   └── tests/
│
├── payments/
│   ├── models.py
│   ├── services.py
│   ├── admin.py
│   └── tests/
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── product-detail.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   ├── register.html
│   └── review_edit.html
│
├── static/
├── media/
│
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Требования

Для запуска проекта локально необходимы:

* Python 3.12 или выше;
* Git.

Для запуска PostgreSQL через Docker дополнительно необходимы:

* Docker;
* Docker Compose.

---

## Установка

### 1. Клонирование репозитория

```powershell
git clone https://github.com/aolgakazakova-max/my_hop_django.git
cd my_hop_django
```

### 2. Создание виртуального окружения

Windows PowerShell:

```powershell
python -m venv .venv
```

Активация:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Установка зависимостей

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Настройка окружения

В корне проекта необходимо создать файл `.env`.

В качестве основы используется файл `.env.example`.

```powershell
Copy-Item .env.example .env
```

После этого при необходимости измените значения переменных в `.env`.

### Переменные окружения

```text
DJANGO_SECRET_KEY
ADMIN_EMAIL
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
```

Файл `.env` содержит локальные настройки и секретные данные и не должен загружаться в Git.

---

## Запуск проекта

В режиме локальной разработки проект использует SQLite.

Перед первым запуском необходимо выполнить миграции:

```powershell
python manage.py migrate
```

Создать администратора:

```powershell
python manage.py createsuperuser
```

Запустить сервер:

```powershell
python manage.py runserver
```

После запуска сайт доступен по адресу:

```text
http://127.0.0.1:8000/
```

Панель администратора:

```text
http://127.0.0.1:8000/admin/
```

---

## PostgreSQL и Docker

Проект поддерживает PostgreSQL и Docker Compose.

Запуск контейнеров:

```powershell
docker compose up -d
```

Проверка состояния контейнеров:

```powershell
docker compose ps
```

Применение миграций:

```powershell
docker compose exec web python manage.py migrate
```

Создание суперпользователя:

```powershell
docker compose exec web python manage.py createsuperuser
```

Остановка контейнеров:

```powershell
docker compose down
```

Для остановки контейнеров с удалением volumes:

```powershell
docker compose down -v
```

---

## Миграции

Создание миграций после изменения моделей:

```powershell
python manage.py makemigrations
```

Применение миграций:

```powershell
python manage.py migrate
```

Просмотр состояния миграций:

```powershell
python manage.py showmigrations
```

---

## Django Admin

Для работы с административной панелью необходимо создать суперпользователя:

```powershell
python manage.py createsuperuser
```

После запуска сервера административная панель доступна по адресу:

```text
http://127.0.0.1:8000/admin/
```

Через Django Admin можно управлять:

* товарами;
* категориями;
* заказами;
* товарами в заказах;
* пользователями;
* профилями;
* отзывами;
* платежами.

---

## Корзина

Корзина реализована с использованием Django sessions.

Пользователь может:

* добавить товар в корзину;
* изменить количество товара;
* удалить товар;
* очистить корзину;
* увидеть общую стоимость заказа.

При добавлении и изменении количества выполняется проверка остатка товара.

Пользователь не может добавить в корзину больше товара, чем доступно на складе.

---

## Оформление заказа

Оформление заказа доступно авторизованному пользователю.

Форма оформления заказа содержит:

* имя;
* номер телефона;
* город;
* адрес;
* способ оплаты.

При создании заказа:

1. Проверяется наличие товара на складе.
2. Рассчитывается общая стоимость.
3. Создаётся заказ.
4. Создаются позиции заказа.
5. Уменьшается количество товара на складе.
6. Создаётся платёж.
7. Обрабатывается mock-платёж.
8. Обновляется статус заказа.
9. Пользователю отправляется email с информацией о заказе.
10. Администратору отправляется уведомление, если указан `ADMIN_EMAIL`.
11. Корзина очищается.

Создание заказа выполняется внутри транзакции базы данных.

---

## Платежи

Для работы с платежами используется отдельное приложение `payments`.

В проекте реализован mock-платёжный сервис.

Поддерживаются способы оплаты:

* банковская карта;
* Wallet;
* оплата при получении.

Статусы платежа:

```text
pending
paid
failed
```

Для банковской карты и Wallet mock-платёж переводится в статус `paid`.

Для оплаты при получении используется статус `pending`.

Платёж связан с заказом отношением `OneToOne`.

Реальная платёжная система в проекте не подключена.

---

## Пользователи и профиль

Пользователь может:

* зарегистрироваться;
* войти в аккаунт;
* выйти из аккаунта;
* просмотреть профиль;
* изменить данные профиля;
* просмотреть свои заказы.

Профиль содержит:

* полное имя;
* номер телефона;
* город;
* адрес.

---

## Отзывы

Авторизованный пользователь может оставить отзыв на товар после его покупки.

Отзыв содержит:

* оценку от 1 до 5;
* комментарий;
* пользователя;
* дату создания.

Для одного пользователя и одного товара разрешён только один отзыв.

Пользователь может:

* создать свой отзыв;
* редактировать свой отзыв;
* удалить свой отзыв.

Отзывы других пользователей нельзя редактировать или удалять.

---

## REST API

Для API используется Django REST Framework.

API предоставляет работу с основными ресурсами проекта:

* товары;
* заказы;
* пользователи;
* корзина;
* отзывы.

Защищённые API endpoints используют аутентификацию.

---

## JWT-аутентификация

Для API используется JWT-аутентификация.

Основные endpoints:

```text
/api/token/
/api/token/refresh/
```

После получения access token он передаётся в HTTP-заголовке:

```text
Authorization: Bearer <access_token>
```

Refresh token используется для получения нового access token.

---

## OpenAPI и Swagger

Документация REST API генерируется с помощью `drf-spectacular`.

В проекте настроена OpenAPI-схема и Swagger UI.

Точные URL документации определяются в `config/urls.py`.

Swagger позволяет просматривать доступные API endpoints, параметры запросов и ответы API.

---

## Тестирование

Для проекта реализованы автоматические тесты Django.

Запуск всех тестов:

```powershell
python manage.py test
```

Тестами покрываются:

* корзина;
* бизнес-логика заказов;
* checkout;
* товары;
* пользователи;
* отзывы;
* платежи;
* REST API;
* аутентификация;
* работа сервисов.

Текущая тестовая коллекция содержит **131 тест**.

Последний полный локальный запуск:

```text
Ran 131 tests

OK
```

---

## Проверка качества кода

### Ruff

Для проверки стиля и качества Python-кода используется Ruff.

Запуск проверки:

```powershell
ruff check .
```

Текущий проект проходит проверку без ошибок:

```text
All checks passed!
```

Для автоматического исправления поддерживаемых проблем:

```powershell
ruff check . --fix
```

---

## Проверка типизации

Для статической проверки типов используется mypy.

Запуск:

```powershell
mypy .
```

Текущий проект проходит проверку:

```text
Success: no issues found in 70 source files
```

---

## Django System Check

Проверка конфигурации Django:

```powershell
python manage.py check
```

Команда должна завершиться без ошибок.

---

## CI GitHub Actions

Для автоматической проверки проекта используется GitHub Actions.

Workflow находится в:

```text
.github/workflows/ci.yml
```

CI запускается:

* при push в `main`;
* при создании Pull Request в `main`.

В CI выполняются:

1. Получение исходного кода из GitHub.
2. Установка Python.
3. Установка зависимостей.
4. Запуск PostgreSQL.
5. Проверка Django.
6. Выполнение миграций.
7. Запуск всех тестов.

Для CI используется отдельный файл настроек:

```text
config/settings/ci.py
```

CI работает с PostgreSQL.

---

## Полезные команды

### Запуск сервера

```powershell
python manage.py runserver
```

### Проверка Django

```powershell
python manage.py check
```

### Создание миграций

```powershell
python manage.py makemigrations
```

### Применение миграций

```powershell
python manage.py migrate
```

### Создание администратора

```powershell
python manage.py createsuperuser
```

### Запуск тестов

```powershell
python manage.py test
```

### Ruff

```powershell
ruff check .
```

### Mypy

```powershell
mypy .
```

### Django shell

```powershell
python manage.py shell
```

### Git status

```powershell
git status
```

### Git pull

```powershell
git pull
```

### Git push

```powershell
git push
```

---

## Безопасность

Секретные данные должны храниться в переменных окружения.

Файл `.env` не должен попадать в Git.

Также в репозиторий не должны попадать:

```text
.env
.venv/
__pycache__/
.idea/
```

Для production необходимо дополнительно настроить:

* `DEBUG=False`;
* безопасный `DJANGO_SECRET_KEY`;
* `ALLOWED_HOSTS`;
* HTTPS;
* secure cookies;
* production database;
* production email settings;
* хранение static/media файлов.

---

## Статус проекта

Основная версия проекта `main` содержит:

* Django интернет-магазин;
* каталог товаров;
* поиск;
* фильтрацию;
* сортировку;
* изображения товаров;
* контроль остатков;
* сессионную корзину;
* оформление заказов;
* историю заказов;
* регистрацию и авторизацию;
* личный кабинет;
* отзывы;
* mock-платежи;
* email-уведомления;
* Django REST Framework API;
* JWT-аутентификацию;
* OpenAPI/Swagger;
* PostgreSQL;
* Docker Compose;
* Django Admin;
* автоматические тесты;
* Ruff;
* mypy;
* GitHub Actions CI.

GraphQL в основную версию проекта не входит.

GraphQL планируется разрабатывать отдельно в ветке `graphql`.

---

## Назначение проекта

Проект создан в учебных целях для демонстрации разработки интернет-магазина на Django и Django REST Framework, включая веб-интерфейс, REST API, работу с базой данных, авторизацию, тестирование и автоматическую проверку качества кода.

---

## Лицензия

Проект предназначен для учебных и портфолио-целей.
