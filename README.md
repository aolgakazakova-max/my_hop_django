# Hop & Barley — интернет-магазин

Full-stack веб-приложение интернет-магазина, разработанное на Django.

Проект представляет собой интернет-магазин пива с каталогом товаров, корзиной, оформлением заказов, личным кабинетом пользователей, отзывами, REST API и GraphQL API.

В проекте реализованы PostgreSQL, Docker Compose, JWT-аутентификация, автоматические тесты, статический анализ кода и CI/CD через GitHub Actions.

---

## Содержание

* [Описание проекта](#описание-проекта)
* [Основные возможности](#основные-возможности)
* [Технологии](#технологии)
* [Структура проекта](#структура-проекта)
* [Требования](#требования)
* [Установка](#установка)
* [Переменные окружения](#переменные-окружения)
* [Запуск локально](#запуск-локально)
* [Запуск через Docker Compose](#запуск-через-docker-compose)
* [База данных и миграции](#база-данных-и-миграции)
* [Django Admin](#django-admin)
* [Каталог товаров](#каталог-товаров)
* [Корзина](#корзина)
* [Заказы и оформление](#заказы-и-оформление)
* [Пользователи и аутентификация](#пользователи-и-аутентификация)
* [Отзывы](#отзывы)
* [Платежи](#платежи)
* [REST API](#rest-api)
* [JWT-аутентификация](#jwt-аутентификация)
* [Swagger и OpenAPI](#swagger-и-openapi)
* [GraphQL API](#graphql-api)
* [Аналитика](#аналитика)
* [Тестирование](#тестирование)
* [Качество кода](#качество-кода)
* [CI/CD](#cicd)
* [Полезные команды](#полезные-команды)
* [Безопасность](#безопасность)
* [Статус проекта](#статус-проекта)

---

# Описание проекта

**Hop & Barley** — интернет-магазин, разработанный на Django.

Приложение предоставляет два основных способа работы:

1. обычный веб-интерфейс на Django Templates;
2. API-интерфейсы через REST и GraphQL.

Веб-приложение использует Django Sessions для авторизации пользователей и хранения корзины.

REST API реализован с использованием Django REST Framework и JWT-аутентификации.

GraphQL API реализован с использованием Strawberry GraphQL.

Основная база данных проекта — PostgreSQL.

Для запуска проекта в контейнерах используется Docker Compose.

---

# Основные возможности

## Каталог

Реализованы:

* список товаров;
* страница отдельного товара;
* категории;
* поиск;
* фильтрация;
* сортировка;
* пагинация;
* отображение рейтинга;
* отображение остатка товара;
* работа только с активными товарами.

Доступны фильтры:

* по категории;
* по минимальной цене;
* по максимальной цене;
* по поисковому запросу.

Доступна сортировка:

* по новизне;
* по цене по возрастанию;
* по цене по убыванию;
* по рейтингу;
* по названию.

---

# Корзина

Корзина реализована через **Django Session**.

Корзина не является отдельной таблицей базы данных.

В сессии пользователя хранится информация о выбранных товарах и их количестве.

Реализованы:

* добавление товара;
* изменение количества;
* удаление товара;
* очистка корзины;
* проверка остатка;
* расчёт общей стоимости.

REST API корзины:

```text
GET    /api/cart/
POST   /api/cart/
PATCH  /api/cart/
DELETE /api/cart/
```

Та же бизнес-логика корзины используется при оформлении заказа.

---

# Заказы и оформление

Модель заказов состоит из:

* `Order`;
* `OrderItem`.

Основная бизнес-логика создания заказа находится в:

```text
orders.services.create_order()
```

Общий процесс оформления заказа:

```text
Корзина
   ↓
Проверка наличия товара
   ↓
Проверка количества
   ↓
Расчёт общей стоимости
   ↓
Создание Order
   ↓
Создание OrderItem
   ↓
Уменьшение остатка товара
   ↓
Обработка платежа
   ↓
Изменение статуса заказа
   ↓
Отправка уведомления
   ↓
Очистка корзины
```

Создание заказа выполняется внутри транзакции базы данных.

Общий сервис создания заказа используется различными интерфейсами приложения, в том числе REST API и GraphQL API.

Таким образом, разные API используют одну и ту же бизнес-логику оформления заказа.

## Статусы заказа

Используются следующие статусы:

```text
pending
paid
shipped
delivered
canceled
```

## Способы оплаты

Реализованы:

* банковская карта;
* оплата при получении.

Платежи являются демонстрационными.

Реального подключения к банковскому или платёжному сервису нет.

---

# Проверка остатка товара

При оформлении заказа система проверяет, что пользователь не может заказать больше товара, чем есть на складе.

Также учитывается ситуация, когда один и тот же товар несколько раз передан в одном запросе.

Например:

```text
Товар A × 3
Товар A × 4
```

система рассматривает как:

```text
Товар A × 7
```

и сравнивает общее количество с остатком на складе.

Это предотвращает возможность обойти проверку stock повторением одного и того же товара в запросе.

---

# Пользователи и аутентификация

Реализованы:

* регистрация;
* вход по email;
* выход;
* личный кабинет;
* редактирование профиля;
* изменение пароля;
* история заказов.

В веб-приложении используется стандартная Django Session Authentication.

REST API использует JWT-аутентификацию.

Защищённые GraphQL-операции требуют авторизации пользователя.

---

# Отзывы

Пользователь может оставить отзыв на товар.

Отзыв содержит:

* оценку от 1 до 5;
* комментарий;
* дату создания;
* пользователя;
* товар.

Правила:

* один пользователь может оставить только один отзыв на один товар;
* пользователь может редактировать свой отзыв;
* оценку можно изменить;
* комментарий можно изменить;
* товар существующего отзыва изменить нельзя;
* пользователя существующего отзыва изменить нельзя.

Уникальность комбинации `user + product` дополнительно контролируется на уровне базы данных.

Средняя оценка товара рассчитывается на основании отзывов.

---

# Технологии

| Технология            | Назначение             |
| --------------------- | ---------------------- |
| Python 3.13           | Язык программирования  |
| Django 6.1            | Web-фреймворк          |
| Django REST Framework | REST API               |
| Simple JWT            | JWT-аутентификация     |
| drf-spectacular       | Swagger / OpenAPI      |
| Strawberry GraphQL    | GraphQL API            |
| PostgreSQL 16         | База данных            |
| Docker                | Контейнеризация        |
| Docker Compose        | Запуск приложения и БД |
| Django Test Framework | Автоматические тесты   |
| Ruff                  | Проверка качества кода |
| mypy                  | Статическая типизация  |
| Git                   | Контроль версий        |
| GitHub Actions        | CI/CD                  |

---

# Структура проекта

Основная структура проекта:

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
├── orders/
├── users/
├── reviews/
├── graphql_api/
│
├── templates/
│
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

Назначение основных приложений:

```text
products/     → каталог и товары
orders/       → корзина, заказы и оформление
users/        → пользователи и профили
reviews/      → отзывы
graphql_api/  → GraphQL API
config/       → настройки Django
templates/    → HTML-шаблоны
```

---

# Требования

Для локального запуска без Docker необходимы:

* Python 3.13 или выше;
* PostgreSQL 16;
* Git.

Для запуска через Docker:

* Docker Desktop;
* Docker Compose.

---

# Установка

Клонировать репозиторий:

```bash
git clone https://github.com/aolgakazakova-max/my_hop_django.git
```

Перейти в каталог проекта:

```bash
cd my_hop_django
```

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Активировать виртуальное окружение в Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

---

# Переменные окружения

Для локальной разработки используется файл `.env`.

Пример:

```env
SECRET_KEY=your-secret-key
DEBUG=True

POSTGRES_DB=hop_django
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

ADMIN_EMAIL=admin@example.com
```

Файл `.env` не должен добавляться в Git.

---

# Запуск локально

Применить миграции:

```bash
python manage.py migrate
```

Создать администратора:

```bash
python manage.py createsuperuser
```

Запустить сервер:

```bash
python manage.py runserver
```

Приложение будет доступно по адресу:

```text
http://127.0.0.1:8000/
```

---

# Запуск через Docker Compose

Docker Compose содержит два основных сервиса:

```text
web → Django-приложение
db  → PostgreSQL 16
```

Запуск:

```bash
docker compose up --build
```

Проверка контейнеров:

```bash
docker compose ps
```

Приложение:

```text
http://127.0.0.1:8000/
```

PostgreSQL:

```text
localhost:5432
```

## Используемая база данных

В Docker Django подключается к PostgreSQL-контейнеру через имя сервиса:

```text
HOST=db
```

Используемый Django database engine:

```text
django.db.backends.postgresql
```

Таким образом, при запуске через Docker Compose Django использует **PostgreSQL, а не SQLite**.

Проверить настройки базы данных можно командой:

```bash
docker compose exec web python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default'])"
```

## Команды внутри контейнера

Миграции:

```bash
docker compose exec web python manage.py migrate
```

Создание суперпользователя:

```bash
docker compose exec web python manage.py createsuperuser
```

Django shell:

```bash
docker compose exec web python manage.py shell
```

Остановка контейнеров:

```bash
docker compose down
```

---

# База данных и миграции

Создание миграций:

```bash
python manage.py makemigrations
```

Применение миграций:

```bash
python manage.py migrate
```

В Docker:

```bash
docker compose exec web python manage.py migrate
```

В Docker Compose используется:

```text
PostgreSQL 16
```

---

# Django Admin

Административная панель доступна по адресу:

```text
/admin/
```

В административной панели можно управлять:

* товарами;
* категориями;
* заказами;
* позициями заказов;
* пользователями;
* профилями;
* отзывами.

## Аналитика Django Admin

В проекте реализована аналитика непосредственно в Django Admin.

Для товаров отображаются, в частности:

* остаток;
* количество проданных единиц;
* количество заказов;
* выручка;
* средний рейтинг;
* активность товара.

Доступны:

* фильтрация;
* поиск;
* редактирование;
* массовая активация товаров;
* массовая деактивация товаров.

Для заказов реализованы:

* фильтрация по статусу;
* фильтрация по дате;
* поиск;
* работа с позициями заказа;
* отображение информации о выручке;
* административные действия.

---

# Каталог товаров

Главная страница содержит каталог активных товаров.

Поддерживаются:

```text
Поиск
Фильтр по категории
Фильтр по минимальной цене
Фильтр по максимальной цене
Сортировка
Пагинация
```

Варианты сортировки:

```text
newest
price ascending
price descending
rating
name
```

Для товаров отображаются:

* название;
* категория;
* цена;
* остаток;
* рейтинг.

---

# REST API

REST API доступен через:

```text
/api/
```

## Товары

```text
GET /api/products/
GET /api/products/<slug>/
```

API товаров поддерживает фильтрацию, поиск и сортировку.

## Категории

```text
GET /api/categories/
```

## Заказы

```text
GET  /api/orders/
POST /api/orders/
```

## Отзывы

```text
GET    /api/reviews/
POST   /api/reviews/
PATCH  /api/reviews/<id>/
DELETE /api/reviews/<id>/
```

## Пользователи

```text
/api/users/
```

## Корзина

```text
GET    /api/cart/
POST   /api/cart/
PATCH  /api/cart/
DELETE /api/cart/
```

---

# JWT-аутентификация

REST API использует JWT через Simple JWT.

## Получение access и refresh token

```text
POST /api/users/login/
```

## Обновление access token

```text
POST /api/users/refresh/
```

Для доступа к защищённым API используется заголовок:

```text
Authorization: Bearer <access_token>
```

---

# Swagger и OpenAPI

Интерактивная документация Swagger:

```text
/api/docs/
```

OpenAPI schema:

```text
/api/schema/
```

Документация генерируется с помощью `drf-spectacular`.

---

# GraphQL API

GraphQL API реализован с использованием Strawberry GraphQL.

Endpoint:

```text
/graphql/
```

## Queries

Поддерживаются запросы:

```text
categories
products
reviews
profile
orders
cart
```

## Analytics Queries

```text
orderAnalytics
productAnalytics
userAnalytics
```

## Mutations

Поддерживаются:

```text
addToCart
updateCart
removeFromCart
createOrder
```

GraphQL mutation `createOrder` использует общий сервис:

```text
orders.services.create_order()
```

Поэтому оформление заказа через GraphQL использует ту же бизнес-логику проверки stock, платежа и создания заказа, что и другие интерфейсы приложения.

---

# Аналитика

В проекте реализована аналитика на двух уровнях:

1. Django Admin;
2. GraphQL API.

## Django Admin

Администратор может получать информацию о:

* продажах;
* количестве проданных товаров;
* заказах;
* выручке;
* рейтингах;
* остатках товаров.

## GraphQL

Доступны аналитические запросы:

```text
orderAnalytics
productAnalytics
userAnalytics
```

Отменённые заказы не учитываются как завершённые заказы в соответствующей аналитике.

---

# Тестирование

Для тестирования используется встроенный Django Test Framework.

Запуск всех тестов:

```bash
python manage.py test
```

Текущий размер тестового набора:

```text
157 тестов
```

Последняя проверка выполнена непосредственно в Docker Compose с PostgreSQL 16.

Результат:

```text
Found 157 test(s).

Ran 157 tests

OK
```

То есть все **157 тестов успешно проходят на PostgreSQL в Docker-среде**.

Также можно запустить тесты непосредственно внутри Docker:

```bash
docker compose exec web python manage.py test
```

## Что проверяют тесты

Тестами покрыты:

* товары;
* каталог;
* фильтрация;
* сортировка;
* корзина;
* заказы;
* проверка остатка;
* повторяющиеся товары в запросе заказа;
* платежи;
* пользователи;
* аутентификация;
* профили;
* отзывы;
* REST API;
* JWT;
* GraphQL;
* аналитика;
* административная функциональность.

Тесты GraphQL можно запустить отдельно:

```bash
python manage.py test graphql_api
```

---

# Проверка качества кода

Проверка Django:

```bash
python manage.py check
```

Текущий результат:

```text
System check identified no issues (0 silenced).
```

## Ruff

Проверка кода:

```bash
ruff check .
```

## mypy

Статическая проверка типов:

```bash
mypy .
```

---

# CI/CD

Для автоматизации используется GitHub Actions.

CI выполняет:

* установку Python;
* установку зависимостей;
* запуск PostgreSQL;
* применение миграций;
* запуск тестов;
* проверку Ruff;
* проверку mypy.

В CI используется:

```text
PostgreSQL 16
```

Тесты запускаются командой:

```text
python manage.py test
```

Для проекта также настроен CD workflow.

---

# Полезные команды

## Django

Запуск сервера:

```bash
python manage.py runserver
```

Проверка проекта:

```bash
python manage.py check
```

Миграции:

```bash
python manage.py makemigrations
python manage.py migrate
```

Создание администратора:

```bash
python manage.py createsuperuser
```

Django shell:

```bash
python manage.py shell
```

Все тесты:

```bash
python manage.py test
```

---

## Docker Compose

Запуск:

```bash
docker compose up --build
```

Проверка:

```bash
docker compose ps
```

Миграции:

```bash
docker compose exec web python manage.py migrate
```

Тесты:

```bash
docker compose exec web python manage.py test
```

Django shell:

```bash
docker compose exec web python manage.py shell
```

Остановка:

```bash
docker compose down
```

---

# Безопасность

Секретные данные хранятся в переменных окружения.

Файл `.env` не должен попадать в Git.

Также не должны добавляться:

```text
.env
.venv/
__pycache__/
.git/
.idea/
```

Для production рекомендуется использовать:

```text
DEBUG=False
```

и безопасный секретный ключ.

---

# Статус проекта

На текущем этапе реализованы основные требования проекта:

* интернет-магазин на Django;
* каталог товаров;
* поиск;
* фильтрация;
* сортировка;
* пагинация;
* корзина на Django Session;
* оформление заказов;
* проверка остатков;
* защита от заказа большего количества товара при повторении товара в запросе;
* mock-платежи;
* регистрация пользователей;
* авторизация;
* личный кабинет;
* отзывы;
* запрет изменения товара у существующего отзыва;
* REST API;
* JWT-аутентификация;
* Swagger/OpenAPI;
* GraphQL API;
* GraphQL аналитика;
* Django Admin аналитика;
* PostgreSQL 16;
* Docker Compose;
* автоматические тесты;
* Ruff;
* mypy;
* GitHub Actions CI/CD.

## Финальная проверка

Проект проверен в Docker Compose:

```text
Django check       → OK
Database           → PostgreSQL 16
Docker Compose     → OK
Automated tests    → 157 passed
SQLite             → не используется в Docker
```

