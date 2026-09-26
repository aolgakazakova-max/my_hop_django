# Hop & Barley

Интернет-магазин продукции из хмеля, разработанный на Django.

Проект представляет собой полноценное веб-приложение интернет-магазина с каталогом товаров, корзиной на основе Django Session, оформлением заказов, личным кабинетом, отзывами, mock-платежами, REST API, JWT-аутентификацией и GraphQL API.

Проект также включает PostgreSQL, Docker Compose, автоматические тесты, статический анализ кода и CI/CD через GitHub Actions.

---

## Содержание

* [Возможности проекта](#возможности-проекта)
* [Технологии](#технологии)
* [Структура проекта](#структура-проекта)
* [Требования](#требования)
* [Установка](#установка)
* [Настройка переменных окружения](#настройка-переменных-окружения)
* [Запуск проекта](#запуск-проекта)
* [Docker Compose](#docker-compose)
* [Миграции](#миграции)
* [Django Admin](#django-admin)
* [Корзина](#корзина)
* [Оформление заказа](#оформление-заказа)
* [Пользователи и авторизация](#пользователи-и-авторизация)
* [Отзывы](#отзывы)
* [REST API](#rest-api)
* [JWT-аутентификация](#jwt-аутентификация)
* [Swagger / OpenAPI](#swagger--openapi)
* [GraphQL API](#graphql-api)
* [Тестирование](#тестирование)
* [Качество кода](#качество-кода)
* [CI/CD](#cicd)
* [Полезные команды](#полезные-команды)
* [Безопасность](#безопасность)
* [Статус проекта](#статус-проекта)

---

## Возможности проекта

### Каталог товаров

* просмотр списка товаров;
* просмотр страницы отдельного товара;
* категории товаров;
* поиск;
* фильтрация по категории и цене;
* сортировка;
* отображение рейтинга товаров;
* пагинация;
* контроль наличия товара на складе.

### Корзина

* добавление товара в корзину;
* изменение количества;
* удаление товара;
* очистка корзины;
* проверка количества товара на складе;
* автоматический пересчёт общей стоимости.

Корзина реализована с использованием **Django Session** и не хранится в отдельной модели базы данных.

### Заказы

* оформление заказа;
* создание `Order` и `OrderItem`;
* проверка наличия товара;
* уменьшение количества товара на складе;
* расчёт стоимости заказа;
* статусы заказа;
* выбор способа оплаты;
* отправка email пользователю и администратору;
* очистка корзины после успешного оформления.

### Пользователи

* регистрация;
* вход по email;
* выход из аккаунта;
* личный профиль;
* редактирование профиля;
* изменение пароля;
* просмотр истории заказов.

### Отзывы

* оценка товара от 1 до 5;
* текстовый комментарий;
* один отзыв пользователя на один товар;
* редактирование только собственного отзыва;
* отображение среднего рейтинга товара.

### Платежи

В проекте используется **mock-платёжная система**.

Реальные банковские платежи не выполняются.

Поддерживаются:

* оплата картой — mock debit payment;
* оплата при получении — Cash on Delivery.

---

## Технологии

* **Python 3.13**
* **Django 6.1**
* **Django REST Framework**
* **Simple JWT**
* **drf-spectacular**
* **Strawberry GraphQL**
* **PostgreSQL 16**
* **Docker**
* **Docker Compose**
* **Ruff**
* **mypy**
* **Django Test Framework**
* **GitHub Actions**
* **Git / GitHub**

---

## Структура проекта

Основные приложения проекта:

```text
hop_django/
│
├── config/
│   └── settings/
│       ├── base.py
│       ├── development.py
│       ├── ci.py
│       └── prod.py
│
├── products/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── ...
│
├── orders/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── serializers.py
│   └── ...
│
├── users/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── ...
│
├── reviews/
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── payments/
│   └── ...
│
├── graphql_api/
│   └── ...
│
├── templates/
│   ├── home.html
│   ├── product-detail.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   ├── register.html
│   └── ...
│
├── static/
├── media/
│
├── manage.py
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Требования

Для локального запуска проекта необходимы:

* Python 3.13
* Git

Для запуска PostgreSQL через Docker:

* Docker Desktop
* Docker Compose

---

## Установка

Клонировать репозиторий:

```powershell
git clone https://github.com/aolgakazakova-max/my_hop_django.git
```

Перейти в директорию проекта:

```powershell
cd my_hop_django
```

Создать виртуальное окружение:

```powershell
python -m venv .venv
```

Активировать виртуальное окружение в PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установить зависимости:

```powershell
pip install -r requirements.txt
```

---

## Настройка переменных окружения

Создать файл `.env` на основе `.env.example`:

```powershell
Copy-Item .env.example .env
```

В `.env` необходимо указать настройки проекта и базы данных.

Пример:

```env
DJANGO_SECRET_KEY=change-me
ADMIN_EMAIL=admin@example.com

POSTGRES_DB=hop_django
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Файл `.env` не должен попадать в Git.

Для Git используется `.env.example` без настоящих секретов.

---

## Запуск проекта

### Локальный запуск

После настройки окружения выполнить:

```powershell
python manage.py migrate
```

При необходимости создать администратора:

```powershell
python manage.py createsuperuser
```

Запустить сервер:

```powershell
python manage.py runserver
```

После запуска приложение доступно по адресу:

```text
http://127.0.0.1:8000/
```

---

## Docker Compose

Проект содержит `docker-compose.yml` с двумя основными сервисами:

```text
docker-compose
│
├── web
│   └── Django application
│
└── db
    └── PostgreSQL 16
```

Запустить контейнеры:

```powershell
docker compose up --build
```

Или запустить в фоновом режиме:

```powershell
docker compose up -d --build
```

Проверить состояние контейнеров:

```powershell
docker compose ps
```

Выполнить миграции внутри контейнера:

```powershell
docker compose exec web python manage.py migrate
```

Создать суперпользователя:

```powershell
docker compose exec web python manage.py createsuperuser
```

Остановить контейнеры:

```powershell
docker compose down
```

> `docker compose down -v` также удаляет Docker volumes. Использовать эту команду следует осторожно, поскольку PostgreSQL хранит данные в volume `pg_data`.

---

## Миграции

Создать миграции после изменения моделей:

```powershell
python manage.py makemigrations
```

Применить миграции:

```powershell
python manage.py migrate
```

---

## Django Admin

Административная панель Django позволяет управлять основными данными приложения:

* пользователями;
* профилями;
* товарами;
* категориями;
* заказами;
* позициями заказов;
* отзывами;
* платежами.

Административная панель доступна по адресу:

```text
http://127.0.0.1:8000/admin/
```

---

## Корзина

Корзина реализована с использованием **Django Session**.

Товары и их количество сохраняются в сессии пользователя.

Основные операции:

```text
Add to cart
    ↓
Django Session
    ↓
изменение количества
    ↓
удаление товара
    ↓
очистка корзины
```

Корзина также доступна через REST API и используется GraphQL API.

---

## Оформление заказа

Создание заказа выполняется через сервисный слой:

```text
orders.services.create_order()
```

Основной сценарий:

```text
Корзина
   ↓
Проверка stock
   ↓
Расчёт стоимости
   ↓
Создание Order
   ↓
Создание OrderItem
   ↓
Уменьшение stock
   ↓
Создание Payment
   ↓
Mock payment
   ↓
Обновление статуса
   ↓
Отправка email
   ↓
Очистка корзины
```

Создание заказа выполняется внутри транзакции базы данных.

GraphQL mutation `createOrder` использует существующий сервис `orders.services.create_order()`, поэтому бизнес-логика заказа не дублируется между веб-интерфейсом и GraphQL API.

---

## Пользователи и авторизация

Веб-интерфейс использует стандартную Django session authentication.

Поддерживаются:

* регистрация;
* вход по email;
* выход;
* профиль пользователя;
* редактирование профиля;
* изменение пароля;
* история заказов.

Для REST API используется JWT-аутентификация.

Таким образом, в проекте используются разные механизмы в зависимости от интерфейса:

```text
Web interface
    ↓
Django Session

REST API
    ↓
JWT

GraphQL
    ↓
Django Session
```

---

## Отзывы

Модель `Review` содержит:

* пользователя;
* товар;
* рейтинг от 1 до 5;
* комментарий;
* дату создания.

Для одного пользователя и одного товара разрешён только один отзыв.

Пользователь может редактировать только собственный отзыв.

---

## REST API

REST API реализован с использованием **Django REST Framework**.

Основные API-разделы:

```text
/api/products/
/api/categories/
/api/orders/
/api/reviews/
/api/users/
/api/cart/
```

Корзина поддерживает основные операции:

```text
GET
POST
PATCH
DELETE
```

---

## JWT-аутентификация

Для API используется JWT.

Получение токенов:

```text
POST /api/token/
```

Обновление access token:

```text
POST /api/token/refresh/
```

После получения access token он передаётся в запросах:

```text
Authorization: Bearer <access_token>
```

---

## Swagger / OpenAPI

Документация REST API создаётся с помощью **drf-spectacular**.

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

Swagger позволяет просматривать доступные endpoints, параметры запросов и схемы ответов.

---

## GraphQL API

GraphQL API реализован с использованием **Strawberry GraphQL**.

GraphQL является частью текущей основной ветки `main`.

### Queries

Поддерживаются запросы для:

* категорий;
* товаров;
* отзывов;
* профиля пользователя;
* заказов;
* корзины.

Пример:

```graphql
query {
  products {
    id
    name
    price
    stock
  }
}
```

### Mutations

Поддерживаются операции:

* `addToCart`;
* `updateCart`;
* `removeFromCart`;
* `createOrder`.

Пример:

```graphql
mutation {
  addToCart(productId: 1, quantity: 2) {
    ...
  }
}
```

GraphQL использует существующую бизнес-логику проекта, в том числе сервис `orders.services.create_order()`.

---

## Тестирование

Для запуска всех тестов:

```powershell
python manage.py test
```

Тестами покрываются основные части проекта:

* корзина;
* товары;
* заказы;
* оформление заказа;
* пользователи;
* авторизация;
* отзывы;
* платежи;
* REST API;
* JWT-аутентификация;
* сервисный слой;
* GraphQL API.

Текущий полный набор тестов проекта:

```text
141 tests
```

Последний успешный локальный запуск:

```text
141 tests OK
```

Для запуска тестов отдельного приложения можно использовать:

```powershell
python manage.py test graphql_api
```

---

## Качество кода

### Django check

Проверка конфигурации Django:

```powershell
python manage.py check
```

### Ruff

Проверка Python-кода:

```powershell
ruff check .
```

Автоматическое исправление поддерживаемых проблем:

```powershell
ruff check . --fix
```

### Mypy

Проверка типов:

```powershell
mypy .
```

---

## CI/CD

Проект использует **GitHub Actions**.

### CI

CI автоматически выполняет проверки проекта при работе с репозиторием.

Основные этапы:

```text
Push / Pull Request
        ↓
GitHub Actions
        ↓
Установка Python
        ↓
Установка зависимостей
        ↓
Запуск PostgreSQL
        ↓
Django checks
        ↓
Миграции
        ↓
Тесты
        ↓
Результат
```

Для CI используется отдельный набор настроек:

```text
config.settings.ci
```

CI также проверяет проект с PostgreSQL.

### CD

В проекте настроен отдельный workflow для CD.

После успешного прохождения необходимых проверок выполняется автоматизированный CD workflow.

---

## Полезные команды

Запуск Django:

```powershell
python manage.py runserver
```

Проверка Django:

```powershell
python manage.py check
```

Создание миграций:

```powershell
python manage.py makemigrations
```

Применение миграций:

```powershell
python manage.py migrate
```

Создание администратора:

```powershell
python manage.py createsuperuser
```

Запуск тестов:

```powershell
python manage.py test
```

Ruff:

```powershell
ruff check .
```

Mypy:

```powershell
mypy .
```

Django shell:

```powershell
python manage.py shell
```

Проверка Git:

```powershell
git status
```

Получение изменений:

```powershell
git pull
```

Отправка изменений:

```powershell
git push
```

Docker:

```powershell
docker compose up --build
```

Проверка контейнеров:

```powershell
docker compose ps
```

Остановка контейнеров:

```powershell
docker compose down
```

---

## Безопасность

Секретные данные не должны храниться в Git.

В `.gitignore` исключены:

```text
.env
.venv/
__pycache__/
.idea/
```

Для production необходимо дополнительно настроить:

* `DEBUG=False`;
* безопасный `SECRET_KEY`;
* `ALLOWED_HOSTS`;
* HTTPS;
* secure cookies;
* production database;
* production email configuration;
* корректную настройку static/media files.

---

## Статус проекта

Текущая основная ветка:

```text
main
```

В текущую версию проекта входят:

* Django web application;
* каталог товаров;
* категории;
* поиск, фильтрация и сортировка;
* session-based корзина;
* оформление заказов;
* mock-платежи;
* личный кабинет;
* отзывы;
* REST API;
* JWT-аутентификация;
* Swagger / OpenAPI;
* GraphQL API;
* PostgreSQL;
* Docker Compose;
* автоматические тесты;
* Ruff;
* mypy;
* GitHub Actions CI;
* GitHub Actions CD.

GraphQL уже объединён с основной веткой `main` и является частью текущей версии проекта.

Последний локальный результат тестирования:

```text
141 tests OK
```

Проект готов для дальнейшей проверки требований технического задания и демонстрации преподавателю.
