import shutil
import uuid
from pathlib import Path

from sqlalchemy import select

from app.database.connection import get_session
from app.database.models import Signature
from app.settings import SIGNATURES_IMAGES


class SignaturesRepository:
    def get_all(self) -> list[Signature]:

        with get_session() as session:

            return session.scalars(select(Signature).order_by(Signature.name)).all()

    def get_by_id(
        self,
        signature_id: int,
    ) -> Signature | None:

        with get_session() as session:

            return session.get(
                Signature,
                signature_id,
            )

    def search(
        self,
        query: str,
    ) -> list[Signature]:

        query = query.strip()

        with get_session() as session:

            statement = select(Signature)

            if query:

                statement = statement.where(Signature.name.ilike(f"%{query}%"))

            statement = statement.order_by(Signature.name)

            return session.scalars(statement).all()

    def add(self, name: str, source_image: str | Path, tax_id: str) -> Signature:

        name = name.strip()

        if not name:
            raise ValueError("Не вказано ПІБ.")

        tax_id = tax_id.strip()

        if not tax_id:
            raise ValueError("Не вказано ІПН.")

        source_image = Path(source_image)

        if not source_image.exists():
            raise FileNotFoundError("Файл підпису не знайдено.")

        allowed_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
        }

        extension = source_image.suffix.lower()

        if extension not in allowed_extensions:
            raise ValueError("Дозволені формати: " "PNG, JPG, JPEG, BMP.")

        SIGNATURES_IMAGES.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_name = f"{uuid.uuid4().hex}{extension}"

        destination = SIGNATURES_IMAGES / file_name

        shutil.copy2(
            source_image,
            destination,
        )

        try:

            with get_session() as session:

                signature = Signature(
                    name=name,
                    file_name=file_name,
                    tax_id=tax_id,
                )

                session.add(signature)

                session.commit()

                session.refresh(signature)

                return signature

        except Exception:

            if destination.exists():
                destination.unlink()

            raise

    def update(
        self,
        signature_id: int,
        name: str,
        tax_id: str,
    ):
        name = name.strip()
        tax_id = tax_id.strip()

        if not name:
            raise ValueError("Не вказано ПІБ.")

        if not tax_id:
            raise ValueError("Не вказано ІПН.")

        if not tax_id.isdigit():
            raise ValueError("ІПН повинен містити тільки цифри.")

        with get_session() as session:
            signature = session.get(
                Signature,
                signature_id,
            )

            if signature is None:
                return None

            signature.name = name
            signature.tax_id = tax_id

            session.commit()
            session.refresh(signature)

            return signature

    def delete(
        self,
        signature_id: int,
    ) -> bool:

        with get_session() as session:

            signature = session.get(
                Signature,
                signature_id,
            )

            if signature is None:
                return False

            image_path = SIGNATURES_IMAGES / signature.file_name

            session.delete(signature)

            session.commit()

        if image_path.exists():
            image_path.unlink()

        return True

    def get_image_path(
        self,
        signature: Signature,
    ) -> Path:

        return SIGNATURES_IMAGES / signature.file_name
