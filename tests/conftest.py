"""
Pytest configuration and fixtures for the Contacts API tests.
"""
import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fakeredis import FakeRedis

from src.main import app
from src.database import Base, get_db
from src import models


# Test database URL - use SQLite in memory for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create a fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create test client with test database and mocked Redis."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    # Mock Redis for all tests
    with patch('src.redis_client.redis') as mock_redis, \
         patch('src.auth.redis_client') as mock_auth_redis, \
         patch('src.crud.redis_client') as mock_crud_redis:
        
        # Setup mock Redis to return reasonable defaults
        mock_redis_instance = FakeRedis()
        mock_redis.from_url.return_value = mock_redis_instance
        mock_auth_redis.get_cached_user.return_value = None
        mock_auth_redis.cache_user.return_value = None
        mock_crud_redis.cache_reset_token.return_value = None
        mock_crud_redis.invalidate_reset_token.return_value = None
        mock_crud_redis.invalidate_user_cache.return_value = None
        
        with TestClient(app) as test_client:
            yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def fake_redis():
    """Create fake Redis client for tests."""
    return FakeRedis()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from src.crud import create_user
    from src.schemas import UserCreate
    
    user_data = UserCreate(email="test@example.com", password="testpassword123")
    user = create_user(db_session, user_data)
    user.verified = True  # Mark as verified for testing
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """Create a test admin user."""
    from src.crud import create_user
    from src.schemas import UserCreate
    from src.models import UserRole
    
    user_data = UserCreate(email="admin@example.com", password="adminpassword123")
    user = create_user(db_session, user_data)
    user.verified = True
    user.role = UserRole.admin
    db_session.commit()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post("/api/login", data={
        "username": test_user.email,
        "password": "testpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, admin_user):
    """Get authentication headers for admin user."""
    response = client.post("/api/login", data={
        "username": admin_user.email,
        "password": "adminpassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_contact_data():
    """Test contact data."""
    from datetime import date
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "birthday": "1990-01-01",
        "additional_data": "Test contact"
    }