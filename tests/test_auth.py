"""
Unit tests for authentication functions.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import timedelta
from fastapi import HTTPException
from jose import jwt

from src import auth, models, schemas


class TestPasswordFunctions:
    """Test password hashing and verification functions."""
    
    def test_get_password_hash(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = auth.get_password_hash(password)
        
        assert hashed != password  # Should be different from original
        assert len(hashed) > 0  # Should not be empty
        assert hashed.startswith("$2b$")  # bcrypt hash format
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = auth.get_password_hash(password)
        
        assert auth.verify_password(wrong_password, hashed) is False


class TestTokenFunctions:
    """Test JWT token creation and validation."""
    
    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        data = {"sub": "test@example.com"}
        token = auth.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode token to verify contents
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload
    
    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = auth.create_access_token(data, expires_delta)
        
        assert token is not None
        
        # Decode token to verify expiry
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload


class TestGetCurrentUser:
    """Test get_current_user function."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock dependencies for get_current_user."""
        with patch('src.auth.get_db') as mock_get_db, \
             patch('src.auth.redis_client') as mock_redis:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            yield mock_db, mock_redis
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, mock_dependencies):
        """Test getting current user with valid token."""
        mock_db, mock_redis = mock_dependencies
        
        # Create a test user
        test_user = models.User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_pass",
            verified=True,
            role=models.UserRole.user
        )
        
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = test_user
        
        # Mock Redis
        mock_redis.get_cached_user.return_value = None
        mock_redis.cache_user.return_value = None
        
        # Create valid token
        token_data = {"sub": "test@example.com"}
        token = auth.create_access_token(token_data)
        
        # Test the function
        user = await auth.get_current_user(token, mock_db)
        
        assert user == test_user
        mock_redis.get_cached_user.assert_called_once_with(1)
        mock_redis.cache_user.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_user_cached(self, mock_dependencies):
        """Test getting current user from cache."""
        mock_db, mock_redis = mock_dependencies
        
        # Create a test user
        test_user = models.User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_pass",
            verified=True,
            role=models.UserRole.user
        )
        
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = test_user
        
        # Mock Redis to return cached user
        cached_data = {
            "id": 1,
            "email": "test@example.com",
            "avatar": None,
            "verified": True,
            "role": "user"
        }
        mock_redis.get_cached_user.return_value = cached_data
        
        # Create valid token
        token_data = {"sub": "test@example.com"}
        token = auth.create_access_token(token_data)
        
        # Test the function
        user = await auth.get_current_user(token, mock_db)
        
        assert user == test_user
        mock_redis.get_cached_user.assert_called_once_with(1)
        # Should not call cache_user since user was already cached
        mock_redis.cache_user.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_dependencies):
        """Test getting current user with invalid token."""
        mock_db, mock_redis = mock_dependencies
        
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(HTTPException) as exc_info:
            await auth.get_current_user(invalid_token, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_subject(self, mock_dependencies):
        """Test getting current user with token missing subject."""
        mock_db, mock_redis = mock_dependencies
        
        # Create token without subject
        token_data = {"other": "data"}
        token = auth.create_access_token(token_data)
        
        with pytest.raises(HTTPException) as exc_info:
            await auth.get_current_user(token, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self, mock_dependencies):
        """Test getting current user when user doesn't exist in database."""
        mock_db, mock_redis = mock_dependencies
        
        # Mock database query to return None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Create valid token
        token_data = {"sub": "nonexistent@example.com"}
        token = auth.create_access_token(token_data)
        
        with pytest.raises(HTTPException) as exc_info:
            await auth.get_current_user(token, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)


class TestRequireAdmin:
    """Test require_admin dependency."""
    
    def test_require_admin_with_admin_user(self):
        """Test require_admin with admin user."""
        admin_user = models.User(
            id=1,
            email="admin@example.com",
            role=models.UserRole.admin
        )
        
        result = auth.require_admin(admin_user)
        assert result == admin_user
    
    def test_require_admin_with_regular_user(self):
        """Test require_admin with regular user."""
        regular_user = models.User(
            id=1,
            email="user@example.com",
            role=models.UserRole.user
        )
        
        with pytest.raises(HTTPException) as exc_info:
            auth.require_admin(regular_user)
        
        assert exc_info.value.status_code == 403
        assert "Admin access required" in str(exc_info.value.detail)