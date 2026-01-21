# Registratsiya MVP

## Цель
Минимальный продукт: React фронтенд, FastAPI бэкенд, PostgreSQL база, регистрация с хэшированием пароля Argon2id и логированием событий.

## Структура проекта
- frontend
  - src
  - Dockerfile
- backend
  - app
  - alembic
  - tests
  - Dockerfile
- docker-compose.yml
- .env
- .env.example

## Архитектура
Frontend → Backend → DB

```
[React UI] -> [FastAPI /api/register, /api/vhod] -> [PostgreSQL users]
```

## Запуск
```bash
docker compose up --build
```

Frontend: http://localhost:5173

Backend: http://localhost:8000

OpenAPI: http://localhost:8000/docs

## Curl примеры
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"login":"tihiy_kot777","parol":"Super#123"}'
```

```bash
curl -X POST http://localhost:8000/api/vhod \
  -H "Content-Type: application/json" \
  -d '{"login":"tihiy_kot777","parol":"Super#123"}'
```

## Валидация
- login: 3–32, латиница/цифры/._-
- parol: минимум 8, строчная, заглавная, цифра, спецсимвол
- конфликт логина: 409

## База данных
Таблица users
- id (PK)
- login (unique)
- password_hash
- created_at

Миграции через Alembic, запуск внутри контейнера backend.

## Тесты
Автотесты:
```bash
cd backend
pytest
```

Ручные проверки:
1. Открыть http://localhost:5173
2. Ввести логин и пароль по правилам
3. Получить сообщение `user создан`
4. Попробовать зарегистрировать тот же логин → 409
5. Проверить вход через блок Vhod

## Логирование
Бэкенд пишет структурированные JSON-сообщения в stdout, уровни INFO и ERROR.

## Безопасность: что сделано
- Пароли никогда не сохраняются в открытом виде, только Argon2id хэш.
- Уникальный индекс на login защищает от дублирования.
- В логах нет сырого пароля.

## Изюминка
- Отдельный блок Vhod для проверки пароля.
- Генерация случайного логина прямо в UI.
- Два эндпоинта для регистрации: /api/register и /api/registratsiya.

## Фото ветки гита и вклад участников
Сделать скриншот `git log --graph --decorate --oneline` и вставить в этот раздел после командных строк.
Участники: backend, frontend, db.
