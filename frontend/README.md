# Frontend

Автор: Приходько К.

Рекомендуется запускать полный проект из репозитория: https://github.com/itmo-webdev/WEBLABARATORNAYA_FEDOTOVA_A_A

## Запуск через Docker Compose

```bash
docker compose up -d --build frontend
```

Открыть в браузере: http://localhost:5173

## Локальный запуск

```bash
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## E2E проверка через Playwright

```bash
docker compose exec backend sh -lc "RUN_E2E=1 FRONTEND_BASE=http://frontend:5173 pytest -q tests/test_e2e_playwright.py"
```
