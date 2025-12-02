# News API

Простейшая реализация CRUD API на FastAPI для сущностей «пользователь», «новость» и «комментарий». Используется SQLAlchemy и SQLite по умолчанию (можно переключить на Postgres через `DATABASE_URL`). Создание новостей разрешено только для верифицированных авторов.

## Запуск локально
1. Создайте виртуальное окружение Python 3.10+ и активируйте его.
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите сервер разработки:
   ```bash
   uvicorn app.main:app --reload
   ```
4. API будет доступно по адресу `http://127.0.0.1:8000`.

## Примеры использования
Создание пользователя (email уникален):
```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "avatar_url": null, "is_verified_author": true}'
```

Создание новости (требуется `is_verified_author=true` у автора):
```bash
curl -X POST http://127.0.0.1:8000/news/ \
  -H "Content-Type: application/json" \
  -d '{"title": "First", "content": {"body": "Hello"}, "author_id": 1}'
```

Создание комментария:
```bash
curl -X POST http://127.0.0.1:8000/comments/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Nice post", "news_id": 1, "author_id": 1}'
```

Обновление и удаление поддерживаются для всех сущностей через `PATCH /{resource}/{id}` и `DELETE /{resource}/{id}`. Список и получение элемента — `GET /{resource}` и `GET /{resource}/{id}`.

## Описание данных
- Пользователь: `name`, `email` (уникальный), `registered_at`, `is_verified_author`, `avatar_url`.
- Новость: `title`, `content` (JSON), `published_at`, `author_id`, `cover_url`.
- Комментарий: `text`, `news_id`, `author_id`, `created_at`.

## Дальнейшие шаги
Эта реализация покрывает базовый CRUD. Для полного соответствия ТЗ нужно добавить:
- миграции Alembic и мок-данные;
- авторизацию (JWT + GitHub OAuth), роли и управление сессиями;
- кэш Redis и хранение сессий в Redis;
- Celery таски для уведомлений и дайджеста;
- отдельный фронтенд на Vite/React.
