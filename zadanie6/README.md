# Zadanie 6

## Запуск через Docker

```bash
docker compose up -d --build postgres redis backend frontend
```

## Тесты

```bash
docker compose exec backend sh -lc "pytest -q"
docker compose exec backend sh -lc "pytest --cov=app --cov-report=term-missing"
docker compose exec backend sh -lc "RUN_E2E=1 FRONTEND_BASE=http://frontend:5173 pytest -q tests/test_e2e_playwright.py"
```
