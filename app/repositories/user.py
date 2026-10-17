from sqlalchemy import select

from app.database.connection import get_session
from app.database.models.user import User


class UserRepository:

    def get_by_id(self, user_id: int) -> User | None:
        with get_session() as session:
            return session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        with get_session() as session:
            return session.scalar(select(User).where(User.username == username.strip()))

    def user_count(self) -> int:
        with get_session() as session:
            return (
                session.scalar(select(User.id).limit(1)) is not None
                and session.query(User).count()
                or 0
            )

    def list_users(self):
        with get_session() as session:
            return [
                {
                    "id": u.id,
                    "username": u.username,
                    "role": u.role,
                    "is_active": u.is_active,
                }
                for u in session.scalars(select(User).order_by(User.username)).all()
            ]

    def set_user_active(self, user_id: int, active: bool):
        with get_session() as session:
            user = session.get(User, user_id)
            if user:
                user.is_active = active
                session.commit()

    def creaet_user(self, username: str, password_hash: str, role: str) -> int:
        with get_session() as session:
            user = User(username=username, password_hash=password_hash, role=role)
            session.add(user)
            session.commit()
            return user.id

    def change_password(self, user_id: int, password_hash: str):
        with get_session() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("Акаунт не знайдено.")
            user.password_hash = password_hash
            session.commit()
