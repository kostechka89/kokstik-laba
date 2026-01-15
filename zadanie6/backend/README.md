# Backend

Автор: Приходько К.

Рекомендуется запускать полный проект из репозитория: https://github.com/itmo-webdev/Prikhodko_Full

## Запуск через Docker Compose

```bash
docker compose up -d --build backend postgres redis
docker compose logs -f backend
```

## Проверка ручек

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/live
curl -i http://localhost:8000/ready
curl -s http://localhost:8000/metrics
curl -i http://localhost:8000/debug/boom
```

## Тесты

```bash
docker compose exec backend sh -lc "pytest -q"
docker compose exec backend sh -lc "pytest --cov=app --cov-report=term-missing"
docker compose exec backend sh -lc "RUN_E2E=1 FRONTEND_BASE=http://frontend:5173 pytest -q tests/test_e2e_playwright.py"
```

## Логи

```bash
docker compose exec backend sh -lc "ls -la /var/log/app"
docker compose exec backend sh -lc "tail -n 50 /var/log/app/app.jsonl"
docker compose exec backend sh -lc "tail -n 50 /var/log/app/notifications.log"
```
