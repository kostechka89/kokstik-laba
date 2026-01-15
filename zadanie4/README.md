# Zadanie 4

## Запуск через Docker

```bash
docker compose up -d --build postgres redis backend celery_worker celery_beat
docker compose logs -f celery_worker
```

## Проверка уведомлений

```bash
curl -i http://localhost:8000/health
docker compose exec backend sh -lc "tail -n 50 /var/log/app/notifications.log"
```
