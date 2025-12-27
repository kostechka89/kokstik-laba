from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api import auth, comments, news, users
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.metrics import REQUEST_COUNT, REQUEST_LATENCY
from app.db.session import get_engine
from app.services.cache import cache_service


logger = configure_logging()
settings = get_settings()


# Optional integration: do not break app startup if hawk sdk isn't available.
hawk_client = None
if settings.hawk_token:
    try:
        from hawk_python_sdk import Hawk  # type: ignore

        hawk_client = Hawk(settings.hawk_token)
    except Exception:  # noqa: BLE001
        try:
            from hawkcatcher import HawkCatcher  # type: ignore

            hawk_client = HawkCatcher(settings.hawk_token)
        except Exception:  # noqa: BLE001
            hawk_client = None


app = FastAPI(title="News API")


# Allow browser frontend (Vite dev server) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(news.router)
app.include_router(comments.router)
app.include_router(users.router)


def write_metrics_log(payload: dict) -> None:
    with open("metrics.jsonl", "a", encoding="utf-8") as file:
        file.write(json.dumps(payload) + "\n")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    with REQUEST_LATENCY.labels(path=request.url.path).time():
        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "request_error",
                path=str(request.url.path),
                error=str(exc),
                request_id=request_id,
            )
            raise

    response.headers["X-Request-ID"] = request_id
    REQUEST_COUNT.labels(method=request.method, path=request.url.path, status=response.status_code).inc()
    logger.info(
        "request",
        method=request.method,
        path=str(request.url.path),
        status=response.status_code,
        request_id=request_id,
    )
    write_metrics_log(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": str(request.url.path),
            "status": response.status_code,
            "request_id": request_id,
        }
    )
    return response


@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        path=str(request.url.path),
        error=str(exc),
        request_id=getattr(request.state, "request_id", None),
    )
    if hawk_client is not None:
        try:
            # hawk-python-sdk: hawk.send(exc)
            if hasattr(hawk_client, "send"):
                hawk_client.send(exc)
            else:
                hawk_client.send_exception(exc)  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass
    return JSONResponse(status_code=500, content={"detail": "Internal error"})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/live")
def live():
    return {"status": "alive"}


@app.get("/ready")
def ready():
    engine = get_engine()
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except Exception:  # noqa: BLE001
        return JSONResponse(status_code=503, content={"status": "db_unavailable"})

    if cache_service.client is None:
        return JSONResponse(status_code=503, content={"status": "redis_unavailable"})
    try:
        cache_service.client.ping()
    except Exception:  # noqa: BLE001
        return JSONResponse(status_code=503, content={"status": "redis_unavailable"})

    return {"status": "ready"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/debug/hawk")
def debug_hawk():
    raise RuntimeError("Hawk debug error")
