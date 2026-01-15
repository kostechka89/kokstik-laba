# Zadanie 3

## Запуск через Docker

```bash
docker compose up -d --build postgres redis backend
docker compose logs -f backend
```

## Проверка кэша

```bash
curl -i http://localhost:8000/health
curl -s http://localhost:8000/news
curl -s http://localhost:8000/news
```
