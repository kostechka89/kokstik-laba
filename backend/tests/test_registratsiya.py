import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.baza import Base, poluchit_sessiyu
from app.main import app


@pytest.fixture()
def klient():
    dvigatel = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
    sessiya_local = sessionmaker(autocommit=False, autoflush=False, bind=dvigatel)
    Base.metadata.create_all(bind=dvigatel)

    def poluchit_test_sessiyu():
        sessiya = sessiya_local()
        try:
            yield sessiya
        finally:
            sessiya.close()

    app.dependency_overrides[poluchit_sessiyu] = poluchit_test_sessiyu
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_uspeshnaya_registratsiya(klient):
    otvet = klient.post(
        "/api/register",
        json={"login": "test_user", "parol": "Super#123"},
    )
    assert otvet.status_code == 200
    assert otvet.json() == {"message": "user создан"}


def test_dublirovanie_logina(klient):
    klient.post(
        "/api/register",
        json={"login": "dubl", "parol": "Super#123"},
    )
    otvet = klient.post(
        "/api/register",
        json={"login": "dubl", "parol": "Super#123"},
    )
    assert otvet.status_code == 409


def test_slabyy_parol(klient):
    otvet = klient.post(
        "/api/register",
        json={"login": "slabyy", "parol": "123"},
    )
    assert otvet.status_code == 422
