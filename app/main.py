from fastapi import FastAPI

from app.routers import comments, news, users

app = FastAPI(title="News CRUD API")

app.include_router(users.router)
app.include_router(news.router)
app.include_router(comments.router)


@app.get("/")
def healthcheck():
    return {"status": "ok"}
