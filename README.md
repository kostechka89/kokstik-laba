# FastAPI News CRUD

CRUD API для пользователей, новостей и комментариев на базе FastAPI + SQLAlchemy + Alembic.

## Требования

- Python 3.10+
- PostgreSQL 13+

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/newsdb
alembic upgrade head

uvicorn app.main:app --reload
```

## Архитектура

- `app/main.py` — точка входа FastAPI
- `app/models.py` — SQLAlchemy модели
- `app/schemas.py` — Pydantic схемы
- `app/routers/*` — CRUD ручки
- `app/db.py` — подключение к БД и dependency

### Модель данных

```mermaid
erDiagram
    USERS ||--o{ NEWS : writes
    USERS ||--o{ COMMENTS : writes
    NEWS ||--o{ COMMENTS : has

    USERS {
        int id
        string name
        string email
        datetime registered_at
        boolean is_verified
        string avatar_url
    }

    NEWS {
        int id
        string title
        json content
        datetime published_at
        string cover_url
        int author_id
    }

    COMMENTS {
        int id
        string text
        datetime published_at
        int news_id
        int author_id
    }
```

### Миграции

1. `001_create_tables.py` — создаёт таблицы и связи, включая каскадное удаление комментариев при удалении новости.
2. `002_seed_data.py` — добавляет моковые данные (2 пользователя, 1 новость, 1 комментарий).

## Примеры запросов

### Пользователи

Создать пользователя:
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Ivan","email":"ivan@example.com","is_verified":true}'
```

Получить список пользователей:
```bash
curl http://localhost:8000/users
```

### Новости

Создать новость (только для верифицированного пользователя):
```bash
curl -X POST http://localhost:8000/news \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","content":{"text":"Hi"},"author_id":1}'
```

Обновить новость:
```bash
curl -X PUT http://localhost:8000/news/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated title"}'
```

### Комментарии

Создать комментарий:
```bash
curl -X POST http://localhost:8000/comments \
  -H "Content-Type: application/json" \
  -d '{"text":"Nice!","news_id":1,"author_id":2}'
```

Обновить комментарий:
```bash
curl -X PUT http://localhost:8000/comments/1 \
  -H "Content-Type: application/json" \
  -d '{"text":"Updated"}'
```

Удалить новость вместе с комментариями:
```bash
curl -X DELETE http://localhost:8000/news/1
```

## Сценарий использования

1. Запустить сервис и выполнить миграции.
2. Создать пользователей.
3. Создать новость от верифицированного автора.
4. Создать комментарий от другого пользователя.
5. Изменить новость и комментарий.
6. Удалить новость — комментарии удалятся каскадно.
