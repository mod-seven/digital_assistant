from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.settings import get_signatures_db_path


class Base(DeclarativeBase):
    pass


def _make_engine(path: str | Path):
    # URL.create коректно обробляє Windows-шляхи, пробіли та мережеві шляхи.
    url = URL.create("sqlite", database=str(Path(path).expanduser()))
    return create_engine(url, connect_args={"timeout": 10})


database_path = get_signatures_db_path()
engine = _make_engine(database_path)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def configure_database(path: str | Path):
    """Перемикає SQLAlchemy на вказаний файл SQLite."""
    global database_path, engine
    new_path = Path(path).expanduser()
    new_engine = _make_engine(new_path)
    old_engine = engine
    engine = new_engine
    database_path = new_path
    SessionLocal.configure(bind=new_engine)
    old_engine.dispose()
    return new_engine


def test_database_connection(path: str | Path | None = None):
    """Перевіряє доступ до БД без створення таблиць."""
    test_engine = engine if path is None else _make_engine(path)
    try:
        with test_engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    finally:
        if path is not None:
            test_engine.dispose()


def get_session():
    return SessionLocal()


def init_database():
    from app.database.models.signature import Signature  # noqa: F401
    from app.database.models.user import User  # noqa: F401

    Base.metadata.create_all(engine)

    # create_all не додає нові колонки до вже існуючих SQLite-таблиць.
    # Додаємо created_by для баз, створених попередніми версіями програми.
    columns = {column["name"] for column in inspect(engine).get_columns("signatures")}
    if "created_by" not in columns:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE signatures ADD COLUMN created_by VARCHAR(80)"
            )
