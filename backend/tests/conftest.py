import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.auth import get_password_hash
from app.models.user import User
from app.main import app
import datetime
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture()
def test_user(db):
    """Create a test user and return credentials."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("TestPass123"),
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user": user, "password": "TestPass123"}

@pytest.fixture()
def auth_headers(client, test_user):
    """Get authentication headers for API requests."""
    response = client.post(
        "/api/v1/auth/login/json",
        json={"username": test_user["user"].username, "password": test_user["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def sample_book_data():
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": f"978-0-{uuid.uuid4().hex[:9]}",
        "category": "Fiction",
        "total_copies": 2,
        "available_copies": 2,
    }

@pytest.fixture()
def sample_member_data():
    return {
        "membership_id": f"MEM-{uuid.uuid4().hex[:6].upper()}",
        "full_name": "Jane Doe",
        "email": f"jane_{uuid.uuid4().hex[:6]}@example.com",
        "phone": "555-1234",
        "status": "active",
        "joined_date": str(datetime.date.today()),
    }

@pytest.fixture()
def created_book(client, auth_headers, sample_book_data):
    """Create a book and return its data."""
    response = client.post("/api/v1/books", json=sample_book_data, headers=auth_headers)
    return response.json()

@pytest.fixture()
def created_member(client, auth_headers, sample_member_data):
    """Create a member and return its data."""
    response = client.post("/api/v1/members", json=sample_member_data, headers=auth_headers)
    return response.json()

