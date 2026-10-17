from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import ROLE_VIEWER
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default=ROLE_VIEWER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
