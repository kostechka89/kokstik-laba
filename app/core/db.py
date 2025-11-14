from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
        db.commit()  
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()  
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()