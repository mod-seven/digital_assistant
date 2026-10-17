"""Облікові записи та перевірка паролів."""

import hashlib
import hmac
import secrets

from sqlalchemy import Boolean, String, select
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base, get_session

ROLE_ADMIN = "admin"
ROLE_SIGNATURES = "signatures_manager"
ROLE_VIEWER = "viewer"
ROLES = {
    ROLE_ADMIN: "Адміністратор",
    ROLE_SIGNATURES: "Керування підписами",
    ROLE_VIEWER: "Перегляд",
}


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default=ROLE_VIEWER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


# def hash_password(password: str) -> str:
#     salt = secrets.token_bytes(16)
#     digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
#     return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


# def verify_password(password: str, encoded: str) -> bool:
#     try:
#         algorithm, salt_hex, digest_hex = encoded.split("$", 2)
#         if algorithm != "pbkdf2_sha256":
#             return False
#         digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 310_000)
#         return hmac.compare_digest(digest.hex(), digest_hex)
#     except (ValueError, TypeError):
#         return False


# def user_count() -> int:
#     with get_session() as session:
#         return session.scalar(select(User.id).limit(1)) is not None and session.query(User).count() or 0


# def authenticate(username: str, password: str):
#     with get_session() as session:
#         user = session.scalar(select(User).where(User.username == username.strip()))
#         if user and user.is_active and verify_password(password, user.password_hash):
#             return {"id": user.id, "username": user.username, "role": user.role}
#     return None


# def create_user(username: str, password: str, role: str):
#     username = username.strip()
#     if len(username) < 3:
#         raise ValueError("Логін має містити щонайменше 3 символи.")
#     if len(password) < 8:
#         raise ValueError("Пароль має містити щонайменше 8 символів.")
#     if role not in ROLES:
#         raise ValueError("Невідома роль.")
#     with get_session() as session:
#         if session.scalar(select(User.id).where(User.username == username)):
#             raise ValueError("Такий логін уже існує.")
#         user = User(username=username, password_hash=hash_password(password), role=role)
#         session.add(user)
#         session.commit()
#         return user.id


# def list_users():
#     with get_session() as session:
#         return [{"id": u.id, "username": u.username, "role": u.role, "is_active": u.is_active}
#                 for u in session.scalars(select(User).order_by(User.username)).all()]


# def set_user_active(user_id: int, active: bool):
#     with get_session() as session:
#         user = session.get(User, user_id)
#         if user:
#             user.is_active = active
#             session.commit()


# def change_password(user_id: int, password: str):
#     if len(password) < 8:
#         raise ValueError("Пароль має містити щонайменше 8 символів.")
#     with get_session() as session:
#         user = session.get(User, user_id)
#         if not user:
#             raise ValueError("Акаунт не знайдено.")
#         user.password_hash = hash_password(password)
#         session.commit()
