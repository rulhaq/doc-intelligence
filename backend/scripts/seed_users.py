"""Seed initial users for local/dev environments."""
import os
import sys

sys.path.append(".")

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value


def _ensure_user(
    db,
    *,
    email: str,
    username: str,
    password: str,
    full_name: str,
    role: UserRole,
) -> None:
    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing:
        print(f"User already exists: {email}")
        return

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
        auth_provider="local",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    print(f"User created: {email}")


def main() -> None:
    admin_email = _get_env("SEED_ADMIN_EMAIL", "admin@example.com")
    admin_password = _get_env("SEED_ADMIN_PASSWORD", "admin123")
    admin_username = _get_env("SEED_ADMIN_USERNAME", "admin")
    admin_full_name = _get_env("SEED_ADMIN_FULL_NAME", "Admin User")

    user_email = _get_env("SEED_USER_EMAIL", "user@example.com")
    user_password = _get_env("SEED_USER_PASSWORD", "user123")
    user_username = _get_env("SEED_USER_USERNAME", "user")
    user_full_name = _get_env("SEED_USER_FULL_NAME", "Demo User")

    db = SessionLocal()
    try:
        _ensure_user(
            db,
            email=admin_email,
            username=admin_username,
            password=admin_password,
            full_name=admin_full_name,
            role=UserRole.ADMIN,
        )
        _ensure_user(
            db,
            email=user_email,
            username=user_username,
            password=user_password,
            full_name=user_full_name,
            role=UserRole.VIEWER,
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
