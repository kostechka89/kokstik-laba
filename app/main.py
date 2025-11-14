from fastapi import FastAPI
from app.core.config import get_settings
from app.routers import users, news, comments
from app.routers import auth
from app.core.redis_client import init_redis, close_redis

settings = get_settings()
app = FastAPI(title="Vrode Rabochiy News Api", version="1.7.0")

app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(news.router, prefix=settings.API_V1_PREFIX)
app.include_router(comments.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {"status": "ok", "name": settings.APP_NAME}

@app.on_event("startup")
async def on_startup() -> None:
    init_redis()

@app.on_event("shutdown")
async def on_shutdown() -> None:
    close_redis()