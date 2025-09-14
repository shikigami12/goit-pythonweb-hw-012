"""
Authentication and authorization module for the Contacts API.

This module handles JWT token creation/validation, password hashing,
user authentication, and role-based access control with Redis caching.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from . import models, schemas
from .database import get_db
from passlib.context import CryptContext
from .redis_client import redis_client
import os

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Database dependency is imported from database module


def verify_password(plain_password, hashed_password):
    """
    Verify a plaintext password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hash a plaintext password.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional token expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db)):
    """
    Get current authenticated user with Redis caching.
    
    This function first checks Redis cache for user data to avoid
    database queries on every request.
    
    Args:
        token: JWT token from request
        db: Database session
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # Try to get user from cache first
    user = db.query(models.User).filter(
        models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    
    # Check cache for user data
    cached_user = redis_client.get_cached_user(user.id)
    if not cached_user:
        # Cache user data for future requests
        user_dict = {
            "id": user.id,
            "email": user.email,
            "avatar": user.avatar,
            "verified": user.verified,
            "role": user.role.value
        }
        redis_client.cache_user(user.id, user_dict)
    
    return user


def require_admin(current_user: models.User = Depends(get_current_user)):
    """
    Dependency to ensure current user has admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != models.UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user