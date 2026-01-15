# Hello, Secure World

Дисциплина: Веб-безопасность
Курс: 3
Дата: 2026-01-15

## Цель работы

Настроить минимальный FastAPI-сервис с защищающими заголовками CSP и HSTS, проверить их фактическое наличие в ответе и зафиксировать результат. Дополнительно сформировать воспроизводимый запуск и краткие выводы.

## Порядок запуска

1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Описание архитектуры и кода

Сервис состоит из одного модуля `app/main.py`. Маршрут `GET /ping` возвращает JSON с сообщением. Middleware добавляет два заголовка безопасности: CSP и HSTS.

## Зачем нужны CSP и HSTS

CSP ограничивает источники загрузки ресурсов и снижает риск XSS. HSTS принуждает браузер использовать HTTPS, защищая от атак понижения. Без этих заголовков повышается риск внедрения скриптов и перехвата трафика.

## Проверка результата

Команда:

```
curl -i http://localhost:8000/ping
```

Фактический вывод:

```
HTTP/1.1 200 OK
content-type: application/json
content-security-policy: default-src 'self'
strict-transport-security: max-age=31536000; includeSubDomains; preload

{"message":"Hello, Secure World"}
```

## Выводы

Сервис стабильно отвечает на `/ping` и добавляет CSP и HSTS. Требования ТЗ выполнены, запуск воспроизводим.
