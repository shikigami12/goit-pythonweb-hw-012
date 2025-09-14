"""
Unit tests for Redis client functionality.
"""
import pytest
import json
from unittest.mock import patch, MagicMock

from src.redis_client import RedisClient


class TestRedisClient:
    """Test Redis client operations."""
    
    @pytest.fixture
    def redis_client(self):
        """Create Redis client with mocked Redis connection."""
        with patch('src.redis_client.redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.from_url.return_value = mock_redis_instance
            
            client = RedisClient()
            client.redis = mock_redis_instance
            return client, mock_redis_instance
    
    def test_cache_user(self, redis_client):
        """Test caching user data."""
        client, mock_redis = redis_client
        
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "avatar": None,
            "verified": True,
            "role": "user"
        }
        
        client.cache_user(1, user_data, 3600)
        
        mock_redis.setex.assert_called_once_with(
            "user:1", 3600, json.dumps(user_data)
        )
    
    def test_cache_user_default_expiry(self, redis_client):
        """Test caching user data with default expiry time."""
        client, mock_redis = redis_client
        
        user_data = {"id": 1, "email": "test@example.com"}
        
        client.cache_user(1, user_data)
        
        mock_redis.setex.assert_called_once_with(
            "user:1", 3600, json.dumps(user_data)
        )
    
    def test_get_cached_user_found(self, redis_client):
        """Test retrieving cached user data when it exists."""
        client, mock_redis = redis_client
        
        user_data = {"id": 1, "email": "test@example.com"}
        mock_redis.get.return_value = json.dumps(user_data)
        
        result = client.get_cached_user(1)
        
        assert result == user_data
        mock_redis.get.assert_called_once_with("user:1")
    
    def test_get_cached_user_not_found(self, redis_client):
        """Test retrieving cached user data when it doesn't exist."""
        client, mock_redis = redis_client
        
        mock_redis.get.return_value = None
        
        result = client.get_cached_user(1)
        
        assert result is None
        mock_redis.get.assert_called_once_with("user:1")
    
    def test_invalidate_user_cache(self, redis_client):
        """Test invalidating user cache."""
        client, mock_redis = redis_client
        
        client.invalidate_user_cache(1)
        
        mock_redis.delete.assert_called_once_with("user:1")
    
    def test_cache_reset_token(self, redis_client):
        """Test caching password reset token."""
        client, mock_redis = redis_client
        
        email = "test@example.com"
        token = "reset_token_123"
        
        client.cache_reset_token(email, token, 3600)
        
        mock_redis.setex.assert_called_once_with(
            "reset_token:test@example.com", 3600, token
        )
    
    def test_cache_reset_token_default_expiry(self, redis_client):
        """Test caching reset token with default expiry."""
        client, mock_redis = redis_client
        
        client.cache_reset_token("test@example.com", "token123")
        
        mock_redis.setex.assert_called_once_with(
            "reset_token:test@example.com", 3600, "token123"
        )
    
    def test_get_reset_token_found(self, redis_client):
        """Test retrieving reset token when it exists."""
        client, mock_redis = redis_client
        
        mock_redis.get.return_value = "reset_token_123"
        
        result = client.get_reset_token("test@example.com")
        
        assert result == "reset_token_123"
        mock_redis.get.assert_called_once_with("reset_token:test@example.com")
    
    def test_get_reset_token_not_found(self, redis_client):
        """Test retrieving reset token when it doesn't exist."""
        client, mock_redis = redis_client
        
        mock_redis.get.return_value = None
        
        result = client.get_reset_token("test@example.com")
        
        assert result is None
        mock_redis.get.assert_called_once_with("reset_token:test@example.com")
    
    def test_invalidate_reset_token(self, redis_client):
        """Test invalidating reset token."""
        client, mock_redis = redis_client
        
        client.invalidate_reset_token("test@example.com")
        
        mock_redis.delete.assert_called_once_with("reset_token:test@example.com")
    
    @patch.dict('os.environ', {'REDIS_URL': 'redis://custom:6379'})
    def test_redis_client_custom_url(self):
        """Test Redis client initialization with custom URL."""
        with patch('src.redis_client.redis') as mock_redis:
            RedisClient()
            mock_redis.from_url.assert_called_once_with(
                'redis://custom:6379', decode_responses=True
            )
    
    @patch.dict('os.environ', {}, clear=True)
    def test_redis_client_default_url(self):
        """Test Redis client initialization with default URL."""
        with patch('src.redis_client.redis') as mock_redis:
            RedisClient()
            mock_redis.from_url.assert_called_once_with(
                'redis://localhost:6379', decode_responses=True
            )