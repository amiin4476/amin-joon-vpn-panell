
import os
import sys

from .database import Base, engine, SessionLocal
from .models import User
from .security import get_password_hash


def main():
    username = os.getenv("ADMIN_USERNAME", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "")

    if len(username) < 3:
        sys.exit("ADMIN_USERNAME must be at least 3 characters.")

    if len(password) < 12:
        sys.exit("ADMIN_PASSWORD must be at least 12 characters.")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        existing = db.query(User).filter(
            User.username == username
        ).first()

        if existing:
            sys.exit("This username already exists. No changes made.")

        admin = User(
            username=username,
            password_hash=get_password_hash(password),
            full_name="مدیر اصلی",
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
