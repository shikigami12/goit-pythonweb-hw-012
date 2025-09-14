"""
Simple tests to check basic functionality.
"""
import pytest
from src import auth, models


def test_password_hashing():
    """Test password hashing functionality."""
    password = "testpassword123"
    hashed = auth.get_password_hash(password)
    
    assert hashed != password
    assert auth.verify_password(password, hashed) is True
    assert auth.verify_password("wrongpassword", hashed) is False


def test_user_role_enum():
    """Test user role enumeration."""
    assert models.UserRole.user.value == "user"
    assert models.UserRole.admin.value == "admin"


def test_token_creation():
    """Test JWT token creation."""
    data = {"sub": "test@example.com"}
    token = auth.create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)