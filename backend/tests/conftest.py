import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
import datetime

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
def sample_book_data():
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "978-0-000-00000-1",
        "category": "Fiction",
        "total_copies": 2,
        "available_copies": 2,
    }

@pytest.fixture()
def sample_member_data():
    return {
        "membership_id": "MEM-001",
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-1234",
        "status": "active",
        "joined_date": str(datetime.date.today()),
    }
