from app.database.connection import init_database
from app.repositories.signatures import SignaturesRepository

init_database()

repository = SignaturesRepository()

print("База працює!")

signatures = repository.get_all()

for signature in signatures:
    print(
        signature.id,
        signature.name,
        signature.file_name,
    )
