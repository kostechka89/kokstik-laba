# Hello, Secure World

Минимальный FastAPI-сервис с защищающими заголовками CSP и HSTS.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Проверка

```bash
curl -i http://localhost:8000/ping
```
