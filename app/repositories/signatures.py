import shutil
import uuid
from pathlib import Path

from sqlalchemy import select

from app.database.connection import get_session
from app.database.models.signature import Signature
from app.settings import get_signatures_images_dir


class SignaturesRepository:
    def get_all(self, include_inactive: bool = False) -> list[Signature]:
        with get_session() as session:
            statement = select(Signature)
            if not include_inactive:
                statement = statement.where(Signature.is_active.is_(True))
            return session.scalars(statement.order_by(Signature.name)).all()

    def get_by_id(self, signature_id: int) -> Signature | None:
        with get_session() as session:
            return session.get(Signature, signature_id)

    def get_by_tax_id(self, tax_id: str) -> Signature | None:
        with get_session() as session:
            return session.scalar(
                select(Signature).where(
                    Signature.tax_id == tax_id,
                    Signature.is_active.is_(True),
                )
            )

    def search(self, query: str, include_inactive: bool = False) -> list[Signature]:
        query = query.strip()
        with get_session() as session:
            statement = select(Signature)
            if not include_inactive:
                statement = statement.where(Signature.is_active.is_(True))
            if query:
                statement = statement.where(Signature.name.ilike(f"%{query}%"))
            return session.scalars(statement.order_by(Signature.name)).all()

    def add(
        self,
        name: str,
        source_image: str | Path,
        tax_id: str,
        created_by: str | None = None,
    ) -> Signature:
        name = name.strip()
        if not name:
            raise ValueError("Не вказано ПІБ.")
        tax_id = tax_id.strip()
        if not tax_id:
            raise ValueError("Не вказано ІПН.")
        if not tax_id.isdigit():
            raise ValueError("ІПН повинен містити тільки цифри.")

        source_image = Path(source_image)
        if not source_image.exists():
            raise FileNotFoundError("Файл підпису не знайдено.")
        allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp"}
        extension = source_image.suffix.lower()
        if extension not in allowed_extensions:
            raise ValueError("Дозволені формати: PNG, JPG, JPEG, BMP.")

        images_dir = get_signatures_images_dir()
        images_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{uuid.uuid4().hex}{extension}"
        destination = images_dir / file_name
        shutil.copy2(source_image, destination)
        try:
            with get_session() as session:
                signature = Signature(
                    name=name,
                    file_name=file_name,
                    tax_id=tax_id,
                    created_by=created_by,
                    is_active=True,
                )
                session.add(signature)
                session.commit()
                session.refresh(signature)
                return signature
        except Exception:
            if destination.exists():
                destination.unlink()
            raise

    def update(self, signature_id: int, name: str, tax_id: str):
        name = name.strip()
        tax_id = tax_id.strip()
        if not name:
            raise ValueError("Не вказано ПІБ.")
        if not tax_id:
            raise ValueError("Не вказано ІПН.")
        if not tax_id.isdigit():
            raise ValueError("ІПН повинен містити тільки цифри.")
        with get_session() as session:
            signature = session.get(Signature, signature_id)
            if signature is None:
                return None
            signature.name = name
            signature.tax_id = tax_id
            session.commit()
            session.refresh(signature)
            return signature

    def set_active(self, signature_id: int, active: bool) -> bool:
        with get_session() as session:
            signature = session.get(Signature, signature_id)
            if signature is None:
                return False
            signature.is_active = active
            session.commit()
            return True

    def delete_permanently(self, signature_id: int) -> bool:
        """Видаляє запис і файл зображення без можливості відновлення."""
        with get_session() as session:
            signature = session.get(Signature, signature_id)
            if signature is None:
                return False
            image_path = get_signatures_images_dir() / signature.file_name
            session.delete(signature)
            session.commit()
        if image_path.exists():
            image_path.unlink()
        return True

    # Зворотна сумісність: delete тепер лише приховує підпис.
    def delete(self, signature_id: int) -> bool:
        return self.set_active(signature_id, False)

    def get_image_path(self, signature: Signature) -> Path:
        return get_signatures_images_dir() / signature.file_name
