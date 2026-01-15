# Zadanie 5

## Запуск через Docker

```bash
docker compose up -d --build postgres redis backend celery_worker celery_beat prometheus grafana elasticsearch logstash kibana
```

## Проверка метрик и логов

```bash
curl -s http://localhost:8000/metrics
curl -i http://localhost:8000/debug/boom
```

## Интерфейсы

- Grafana: http://localhost:3000
- Kibana: http://localhost:5601
