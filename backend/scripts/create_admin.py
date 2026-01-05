"""Create Admin User Script"""
import sys
import argparse
from sqlalchemy.orm import Session

sys.path.append(".")

from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import hash_password


def create_admin(email: str, password: str, username: str = None):
    """Create admin user"""
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User with email {email} already exists")
            return
        
        # Create admin user
        user = User(
            email=email,
            username=username or email.split("@")[0],
            hashed_password=hash_password(password),
            full_name="Admin User",
            role=UserRole.ADMIN,
            auth_provider="local",
            is_active=True,
            is_verified=True,
        )
        
        db.add(user)
        db.commit()
        
        print(f"Admin user created: {email}")
        
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--username", help="Admin username (optional)")
    
    args = parser.parse_args()
    
    create_admin(args.email, args.password, args.username)

