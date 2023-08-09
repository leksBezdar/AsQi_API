# AsQi_API



## Основные компоненты МОДУЛЯ АВТОРИЗАЦИИ src/auth

### `auth.py`

Модуль для создания и проверки токенов, хеширования паролей и других функций аутентификации.

### `crud.py`

Модуль для выполнения операций CRUD (Создание, Чтение, Обновление, Удаление) с пользователями и ролями в базе данных.

### `models.py`

Определение моделей базы данных, таких как `User` и `Role`, с их полями и отношениями.

### `schemas.py`

Определение схем данных с использованием Pydantic, включая схемы для пользователей и ролей.

### `routers.py`

Определение маршрутов FastAPI для обработки запросов связанных с аутентификацией, авторизацией и управлением пользователями.

### `config.py`

Модуль для настройки параметров приложения, таких как секретный ключ, алгоритм шифрования и сроки действия токенов.

## Запуск проекта

1. Создайте виртуальное окружение venv (python -m venv venv)
2. Активируйте venv (venv/Scripts/activate)
3. Установите зависимости, указанные в файле `requirements.txt` (pip install -r requirements.txt)
4. Создайте базу данных.
5. Укажите необходимые переменные окружения в файле `.env` в корневой директории AsQi, такие как:

    * SECRET_KEY=<ваш_секретный_ключ>
    * ALGORITHM=<алгоритм_шифрования>
    * ACCESS_TOKEN_EXPIRE_MINUTES=<срок_действия_токена_доступа_в_минутах>
    * REFRESH_TOKEN_EXPIRE_DAYS=<срок_действия_токена_обновления_в_днях>
    * DB_HOST=<хост_базы_данных>
    * DB_PORT=<порт_базы_данных>
    * DB_NAME=<имя_базы_данных>
    * DB_USER=<пользователь_базы_данных>
    * DB_PASS=<пароль_пользователя_базы_данных>

6. Проведите миграции, для заполнения полями вашей базы. (alembic upgrade head)
7. Запустите приложение с помощью команды: `uvicorn main:app --host 0.0.0.0 --port 8000`

## Пример использования

Примеры использования эндпоинтов можно найти в файле `routers.py`. ВАЖНО! СНАЧАЛА необходимо создать роли, а уже ПОТОМ пользователей.

## Зависимости

Полный список зависимостей указан в файле `requirements.txt`.
