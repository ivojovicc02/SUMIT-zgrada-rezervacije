from database import SessionLocal
from models.user import User
from auth import get_password_hash


def create_first_admin():
    db = SessionLocal()

    try:
        existing_admin = (
            db.query(User)
            .filter(User.role == "admin")
            .first()
        )

        if existing_admin:
            print("Admin već postoji.")
            return

        admin = User(
            username="admin",
            email="admin@sumit.ba",
            hashed_password=get_password_hash("Admin123!"),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"Admin uspješno kreiran: {admin.username}")

    except Exception as error:
        db.rollback()
        print(f"Greška pri kreiranju admina: {error}")

    finally:
        db.close()


if __name__ == "__main__":
    create_first_admin()