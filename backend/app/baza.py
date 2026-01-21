from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.nastroyki import nastroyki


Base = declarative_base()


dvigatel = create_engine(nastroyki.database_url, pool_pre_ping=True)

Sessiya = sessionmaker(autocommit=False, autoflush=False, bind=dvigatel)


def poluchit_sessiyu():
    sessiya = Sessiya()
    try:
        yield sessiya
    finally:
        sessiya.close()
