from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.settings import SIGNATURES_DB


class Base(DeclarativeBase):
    pass


engine = create_engine(
    f"sqlite:///{SIGNATURES_DB}",
    connect_args={
        "timeout": 10,
    },
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_session():
    return SessionLocal()


def init_database():
    from app.database.models import Signature

    Base.metadata.create_all(engine)
