from fastapi import Depends, FastAPI

from app.dependencies import get_current_user
from app.routers import auth, comments, news, users

app = FastAPI(title="News CRUD API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(news.router)
app.include_router(comments.router)


@app.get("/", dependencies=[Depends(get_current_user)])
def healthcheck():
    return {"status": "ok"}
