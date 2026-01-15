from fastapi import FastAPI, Request, Response

app = FastAPI()


@app.middleware("http")
async def защитные_заголовки(request: Request, call_next):
    ответ = await call_next(request)
    ответ.headers["Content-Security-Policy"] = "default-src 'self'"
    ответ.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return ответ


@app.get("/ping")
async def ping():
    сообщение = "Hello, Secure World"
    return {"message": сообщение}
