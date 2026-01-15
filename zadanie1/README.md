# Zadanie 1

## Запуск через Docker

```bash
docker compose up -d --build postgres backend
docker compose logs -f backend
```

## Проверка

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/live
curl -i http://localhost:8000/ready
```

## Примеры CRUD

```bash
curl -s http://localhost:8000/users
curl -s http://localhost:8000/news
curl -s http://localhost:8000/comments
```
