"""Seed initial users for OpenShift/local environments.

Creates one admin and one regular user (if they don't already exist).
Credentials are controlled via environment variables so they can be provided
via OpenShift Secrets.
"""

import os

from models.database import SessionLocal, User, init_db
from services.auth_service import get_password_hash


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value.strip() if value is not None else default


def _ensure_user(*, username: str, password: str, is_admin: bool) -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"User already exists: {username}")
            return

        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            is_admin=is_admin,
        )
        db.add(user)
        db.commit()
        print(f"User created: {username} (admin={is_admin})")
    finally:
        db.close()


def main() -> None:
    # Ensure tables exist before seeding users.
    init_db()

    admin_username = _get_env("SEED_ADMIN_USERNAME", "admin")
    admin_password = _get_env("SEED_ADMIN_PASSWORD", "admin123")

    user_username = _get_env("SEED_USER_USERNAME", "user")
    user_password = _get_env("SEED_USER_PASSWORD", "user123")

    _ensure_user(username=admin_username, password=admin_password, is_admin=True)
    _ensure_user(username=user_username, password=user_password, is_admin=False)


if __name__ == "__main__":
    main()

