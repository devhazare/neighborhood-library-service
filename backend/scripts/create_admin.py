"""Create default admin user for testing"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.auth import get_password_hash
from app.models.user import User

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("Admin user already exists!")
            return

        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@library.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")

        # Create a regular test user
        test_user = User(
            username="testuser",
            email="test@library.com",
            full_name="Test User",
            hashed_password=get_password_hash("test123"),
            is_active=True,
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        print("✅ Test user created successfully!")
        print("   Username: testuser")
        print("   Password: test123")

    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()

