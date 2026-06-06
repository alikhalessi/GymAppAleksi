from collections.abc import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_SQLITE_DATABASE_URL = "sqlite:///./setpilot.db"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL") or os.getenv("SETPILOT_DATABASE_URL") or DEFAULT_SQLITE_DATABASE_URL


def get_connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


SQLALCHEMY_DATABASE_URL = get_database_url()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=get_connect_args(SQLALCHEMY_DATABASE_URL),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
