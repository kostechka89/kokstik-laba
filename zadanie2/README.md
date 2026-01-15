# Zadanie 2

## Запуск через Docker

```bash
docker compose up -d --build postgres redis backend
docker compose logs -f backend
```

## Проверка авторизации

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/auth/github/login
curl -i http://localhost:8000/auth/login
curl -i http://localhost:8000/auth/refresh
curl -i http://localhost:8000/auth/sessions
```
