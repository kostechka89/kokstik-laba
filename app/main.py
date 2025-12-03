from fastapi import FastAPI

from .database import engine, Base
from .routers import users, news, comments, auth
from .config import get_settings

Base.metadata.create_all(bind=engine)

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(news.router)
app.include_router(comments.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
