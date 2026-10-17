import hashlib
import hmac
import secrets

from app.constants import ROLES
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
        return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"

    def verify_password(self, password: str, encoded: str) -> bool:
        try:
            algorithm, salt_hex, digest_hex = encoded.split("$", 2)
            if algorithm != "pbkdf2_sha256":
                return False
            digest = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 310_000
            )
            return hmac.compare_digest(digest.hex(), digest_hex)
        except (ValueError, TypeError):
            return False

    def authenticate(self, username: str, password: str):
        user = self.user_repository.get_by_username(username)
        if (
            user
            and user.is_active
            and self.verify_password(password, user.password_hash)
        ):
            return {"id": user.id, "username": user.username, "role": user.role}
        return None

    def create_user(self, username: str, password: str, role: str):
        username = username.strip()
        if len(username) < 3:
            raise ValueError("Логін має містити щонайменше 3 символи.")
        if len(password) < 8:
            raise ValueError("Пароль має містити щонайменше 8 символів.")
        if role not in ROLES:
            raise ValueError("Невідома роль.")

        user = self.user_repository.get_by_username(username)
        if user:
            raise ValueError("Такий логін уже існує.")

        return self.user_repository.create_user(
            username, self.hash_password(password), role
        )

    def change_password(self, user_id: int, password: str):
        if len(password) < 8:
            raise ValueError("Пароль має містити щонайменше 8 символів.")
        password_hash = self.hash_password(password)
        self.user_repository.change_password(user_id, password_hash)
