"""
CRUD (Create, Read, Update, Delete) operations for the Contacts API.

This module contains all database operations for users and contacts,
including authentication-related functions, contact management,
and password reset functionality.
"""
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date, timedelta
from .auth import get_password_hash
from .redis_client import redis_client
import uuid


def get_user_by_email(db: Session, email: str):
    """
    Get user by email address.
    
    Args:
        db: Database session
        email: User email address
        
    Returns:
        User model instance or None
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user account.
    
    Args:
        db: Database session
        user: User creation data
        
    Returns:
        Created user model instance
    """
    hashed_password = get_password_hash(user.password)
    verification_token = str(uuid.uuid4())
    db_user = models.User(email=user.email, hashed_password=hashed_password,
                          verification_token=verification_token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_verification_status(db: Session, user: models.User):
    """
    Update user verification status to verified.
    
    Args:
        db: Database session
        user: User model instance to update
        
    Returns:
        Updated user model instance
    """
    user.verified = True
    user.verification_token = None
    db.commit()
    return user


def set_verification_token(db: Session, user: models.User):
    """
    Generate and set new verification token for user.
    
    Args:
        db: Database session
        user: User model instance to update
        
    Returns:
        Updated user model instance with new verification token
    """
    verification_token = str(uuid.uuid4())
    user.verification_token = verification_token
    db.commit()
    return user


def update_avatar(db: Session, user: models.User, url: str):
    """
    Update user avatar URL.
    
    Args:
        db: Database session
        user: User model instance to update
        url: New avatar URL
        
    Returns:
        Updated user model instance
    """
    user.avatar = url
    db.commit()
    return user


def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Get a specific contact by ID for a user.
    
    Args:
        db: Database session
        contact_id: Contact ID to retrieve
        user_id: User ID to filter by
        
    Returns:
        Contact model instance or None if not found
    """
    return db.query(models.Contact).filter(models.Contact.id == contact_id,
                                           models.Contact.user_id == user_id).first()


def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Get paginated list of contacts for a user.
    
    Args:
        db: Database session
        user_id: User ID to filter by
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of contact model instances
    """
    return db.query(models.Contact).filter(
        models.Contact.user_id == user_id).offset(skip).limit(limit).all()


def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    """
    Create a new contact for a user.
    
    Args:
        db: Database session
        contact: Contact creation data
        user_id: User ID who owns the contact
        
    Returns:
        Created contact model instance
    """
    db_contact = models.Contact(**contact.model_dump(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: schemas.ContactCreate,
                   user_id: int):
    """
    Update an existing contact for a user.
    
    Args:
        db: Database session
        contact_id: Contact ID to update
        contact: Updated contact data
        user_id: User ID who owns the contact
        
    Returns:
        Updated contact model instance or None if not found
    """
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id, models.Contact.user_id == user_id).first()
    if db_contact:
        for key, value in contact.model_dump().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Delete a contact for a user.
    
    Args:
        db: Database session
        contact_id: Contact ID to delete
        user_id: User ID who owns the contact
        
    Returns:
        Deleted contact model instance or None if not found
    """
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id, models.Contact.user_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def search_contacts(db: Session, query: str, user_id: int):
    """
    Search contacts by name or email for a user.
    
    Args:
        db: Database session
        query: Search query string
        user_id: User ID to filter by
        
    Returns:
        List of matching contact model instances
    """
    return db.query(models.Contact).filter(
        (models.Contact.first_name.ilike(f"%{query}%")) |
        (models.Contact.last_name.ilike(f"%{query}%")) |
        (models.Contact.email.ilike(f"%{query}%")),
        models.Contact.user_id == user_id
    ).all()


def get_birthdays(db: Session, user_id: int):
    """
    Get contacts with birthdays in the next 7 days.
    
    Args:
        db: Database session
        user_id: User ID to filter contacts
        
    Returns:
        List of contacts with upcoming birthdays
    """
    today = date.today()
    end_date = today + timedelta(days=7)
    return db.query(models.Contact).filter(
        (models.Contact.birthday >= today) &
        (models.Contact.birthday <= end_date),
        models.Contact.user_id == user_id
    ).all()


def create_password_reset_token(db: Session, email: str) -> str:
    """
    Create a password reset token for user.
    
    Args:
        db: Database session
        email: User email address
        
    Returns:
        Reset token string
        
    Raises:
        ValueError: If user not found or not verified
    """
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("User not found")
    if not user.verified:
        raise ValueError("User not verified")
    
    reset_token = str(uuid.uuid4())
    user.reset_token = reset_token
    db.commit()
    
    # Cache token in Redis for 1 hour
    redis_client.cache_reset_token(email, reset_token, 3600)
    
    return reset_token


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """
    Reset user password using reset token.
    
    Args:
        db: Database session
        token: Password reset token
        new_password: New password to set
        
    Returns:
        True if password reset successful, False otherwise
    """
    user = db.query(models.User).filter(models.User.reset_token == token).first()
    if not user:
        return False
    
    # Hash new password and clear reset token
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db.commit()
    
    # Invalidate cached reset token and user cache
    redis_client.invalidate_reset_token(user.email)
    redis_client.invalidate_user_cache(user.id)
    
    return True