# Full stack (Docker) — Windows quickstart

## Requirements
- Windows 10/11
- Docker Desktop (enable WSL2 backend)

## Start (build + run)
From the folder containing `docker-compose.yml`:

```bat
docker compose up -d --build
```

## Check services
- Backend Swagger: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000  (default login admin / admin)
- Kibana: http://localhost:5601
- Elasticsearch: http://localhost:9200

## Logs
```bat
docker compose logs -f backend
docker compose logs -f celery_worker
docker compose logs -f logstash
```

## Stop
```bat
docker compose down
```

## Reset data (DANGER: deletes DB + logs)
```bat
docker compose down -v
```

## Kibana quick check (logs)
1. Open Kibana -> "Discover"
2. Create data view for index pattern: `app-logs-*`
3. You should see JSON events like `event=request` etc.
