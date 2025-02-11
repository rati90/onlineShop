from app.dependencies.auth import hash_password
from app.db.database import  SessionLocal
from app.db.models import Admin
from sqlmodel import select
import os


def seed_admin_if_none_exist():
    # Suppose you read username/password from environment or .env
    admin_username = os.getenv("FIRST_ADMIN_USERNAME")
    admin_password = os.getenv("FIRST_ADMIN_PASSWORD")

    with SessionLocal() as db:
        # Check if there's already an admin in the DB
        existing_admin = db.exec(select(Admin)).first()
        if existing_admin:
            return  # We already have at least one admin, do nothing

        # Otherwise, create the very first admin
        new_admin = Admin(
            username=admin_username,
            hashed_password=hash_password(admin_password),
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print(f"Seeded initial admin user: {new_admin.username}")