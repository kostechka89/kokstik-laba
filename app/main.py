from fastapi import FastAPI

from .database import engine, Base
from .routers import users, news, comments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="News API")

app.include_router(users.router)
app.include_router(news.router)
app.include_router(comments.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
