from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.baza import poluchit_sessiyu
from app.bezopasnost import proverit_parol, sdelat_hash
from app.modeli import Polzovatel
from app.nastroyki import nastroyki
from app.shemy import RegistratsiyaOtvet, RegistratsiyaZapros, VhodOtvet, VhodZapros
from app.zhurnal import nastroit_loger, zapis_eventa


loger = nastroit_loger(nastroyki.app_env)

app = FastAPI(title="Registratsiya MVP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def nayti_polzovatelya(sessiya: Session, login: str) -> Polzovatel | None:
    zapros = select(Polzovatel).where(Polzovatel.login == login)
    return sessiya.execute(zapros).scalar_one_or_none()


@app.post("/api/register", response_model=RegistratsiyaOtvet)
@app.post("/api/registratsiya", response_model=RegistratsiyaOtvet)
def registratsiya(dannye: RegistratsiyaZapros, sessiya: Session = Depends(poluchit_sessiyu)):
    if nayti_polzovatelya(sessiya, dannye.login):
        zapis_eventa(loger, "INFO", "konflikt_login", login=dannye.login)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="login уже занят")
    polzovatel = Polzovatel(login=dannye.login, password_hash=sdelat_hash(dannye.parol))
    sessiya.add(polzovatel)
    try:
        sessiya.commit()
    except IntegrityError:
        sessiya.rollback()
        zapis_eventa(loger, "ERROR", "oshibka_bazy", login=dannye.login)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="login уже занят")
    zapis_eventa(loger, "INFO", "registratsiya_ok", login=dannye.login)
    return RegistratsiyaOtvet(message="user создан")


@app.post("/api/vhod", response_model=VhodOtvet)
def vhod(dannye: VhodZapros, sessiya: Session = Depends(poluchit_sessiyu)):
    polzovatel = nayti_polzovatelya(sessiya, dannye.login)
    if not polzovatel or not proverit_parol(dannye.parol, polzovatel.password_hash):
        zapis_eventa(loger, "INFO", "nevernye_dannye", login=dannye.login)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="неверный логин или пароль")
    zapis_eventa(loger, "INFO", "vhod_ok", login=dannye.login)
    return VhodOtvet(message="vhod выполнен")
