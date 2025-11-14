
# News API

Это REST‑сервер для новостного портала. Сервис реализован на FastAPI, SQLAlchemy и Alembic и поддерживает регистрацию, аутентификацию, работу с новостями и комментариями, а также кэширование сессий и данных через Redis. Доступ к большинству ручек возможен только после получения JWT‑токена.

## Основные сущности

* **Пользователь** – содержит имя, email, флаг verified_author, флаг is_admin, URL аватарки и дату регистрации. Пароль хранится в виде хэша Argon2.
* **Новость** – заголовок, произвольный JSON‑контент, время публикации, идентификатор автора и URL обложки. Создавать новости могут только верифицированные авторы или администраторы, редактировать и удалять – только автор или администратор.
* **Комментарий** – текст, время публикации, ссылка на новость и автора. Комментировать может любой аутентифицированный пользователь, редактировать и удалять – только автор комментария или администратор.

## Аутентификация

Аутентификация основана на JWT. Сервис выдаёт пару токенов – короткоживущий access‑токен и refresh‑токен. Для работы необходимо сначала зарегистрироваться, затем войти и использовать access‑токен в заголовке `Authorization: Bearer <token>`.

### Регистрация и вход

* `POST /api/v1/auth/register` – регистрация нового пользователя. Принимает имя, email, пароль и флаг verified_author. Возвращает данные пользователя.
* `POST /api/v1/auth/login` – вход по email и паролю. Возвращает access и refresh токены.
* `GET /api/v1/auth/github` – начало OAuth‑аутентификации через GitHub. Перенаправляет на форму входа GitHub.
* `GET /api/v1/auth/github/callback` – обработка ответа GitHub, создаёт пользователя при первом входе.
* `POST /api/v1/auth/refresh` – получение новой пары токенов по действующему refresh‑токену.
* `POST /api/v1/auth/logout` – выход и отзыв refresh‑токена.
* `GET /api/v1/auth/sessions` – список активных сессий пользователя с указанием user_agent и срока действия.

### Ролевые ограничения

* Автор (verified_author=True) или администратор (is_admin=True) может создавать новости.
* Редактирование и удаление новости разрешены только её автору или администратору.
* Комментарии может добавлять любой аутентифицированный пользователь. Редактирование и удаление комментария разрешены только его автору или администратору.
* Просмотр и изменение учётных записей пользователей доступны только администратору; пользователь может просматривать и менять только свой профиль.

## Кэширование

Redis используется для двух задач: хранения новостей и хранения сессий. Каждая новость кэшируется по ключу `news:<id>` сроком на пять минут. Сессии пользователей сохраняются по ключам `session:<jti>`, список активных сессий хранится в `user_sessions:<user_id>`. При создании, обновлении или удалении новости кэш обновляется. Данные пользователя без чувствительных полей помещаются в кэш для ускорения проверки авторизации.

## Настройка окружения

Перед запуском необходимо создать файл `.env` в корне проекта и указать переменные:

```
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/news_db
APP_NAME=News API
API_V1_PREFIX=/api/v1
JWT_SECRET_KEY=supersecretkey
GITHUB_CLIENT_ID=<client_id>
GITHUB_CLIENT_SECRET=<client_secret>
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/github/callback
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Установка и запуск

1. Клонируйте репозиторий и установите зависимости.

   ```sh
   git clone <ваш форк репозитория>
   cd Lab1_PrikhodkoK_R-main
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Создайте базу данных и примените миграции.

   ```sh
   psql -U postgres -c "CREATE DATABASE news_db;"
   PYTHONPATH=. alembic upgrade head
   ```

3. Запустите Redis на `REDIS_HOST` и `REDIS_PORT` (например, через `docker run -p 6379:6379 redis`).

4. Запустите приложение.

   ```sh
   uvicorn app.main:app --reload
   ```

Приложение будет доступно по адресу `http://127.0.0.1:8000`. Документация Swagger – `/docs`.

## Примеры запросов

Регистрация пользователя:

```sh
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"name":"Author","email":"author@example.com","password":"secret","verified_author":true}'
```

Вход и получение токенов:

```sh
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"author@example.com","password":"secret"}'
```

Создание новости (access‑токен помещается в заголовок):

```sh
curl -X POST http://127.0.0.1:8000/api/v1/news/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"title":"Первая новость","content":{"text":"Контент новости"},"cover_url":"https://example.com/news1.png"}'
```

Добавление комментария:

```sh
curl -X POST http://127.0.0.1:8000/api/v1/comments/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"news_id":1,"text":"Первый комментарий"}'
```

Обновление новости:

```sh
curl -X PATCH http://127.0.0.1:8000/api/v1/news/1 \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"title":"Обновлённая новость","content":{"text":"Исправленный контент"}}'
```

Удаление новости

```sh
curl -X DELETE http://127.0.0.1:8000/api/v1/news/1
```

---

Проверка валидаций

Создание новости неавторизованным пользователем → 403

```sh
curl -X POST http://127.0.0.1:8000/api/v1/news/ \
    -H "Content-Type: application/json" \
    -d '{"title":"Невалидная","content":{"text":"123"},"author_id":2,"cover_url":"x"}'
```

---

Без title → 422

```sh
curl -X POST http://127.0.0.1:8000/api/v1/news/ \
    -H "Content-Type: application/json" \
    -d '{"content":{"text":"123"},"author_id":1,"cover_url":"x"}'
```

---

Комментарий к несуществующей новости → 404

```sh
curl -X POST http://127.0.0.1:8000/api/v1/comments/ \
    -H "Content-Type: application/json" \
    -d '{"text":"lol","news_id":9999,"author_id":1}'
```

---

Дополнительно
- БД можно заменить на MongoDB через реализацию интерфейсов репозиториев в app/repositories.
- Миграции с тестовыми данными можно добавить отдельным Alembic ревиженом или SQL скриптом.

