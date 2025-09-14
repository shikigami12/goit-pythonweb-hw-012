"""
SQLAlchemy database models for the Contacts API.

This module defines the database schema including User and Contact models
with their relationships and user roles enumeration.
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum


class UserRole(enum.Enum):
    """Enumeration of user roles for role-based access control."""
    user = "user"
    admin = "admin"


class Contact(Base):
    """
    Contact model for storing contact information.
    
    Attributes:
        id: Primary key
        first_name: Contact's first name
        last_name: Contact's last name
        email: Contact's email address (unique)
        phone_number: Contact's phone number
        birthday: Contact's birthday
        additional_data: Optional additional information
        user_id: Foreign key to user who owns this contact
        user: Relationship to User model
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    birthday = Column(Date)
    additional_data = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="contacts")


class User(Base):
    """
    User model for storing user account information.
    
    Attributes:
        id: Primary key
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        avatar: Optional avatar URL
        verified: Whether email is verified
        verification_token: Token for email verification
        role: User role (user or admin)
        reset_token: Token for password reset
        contacts: Relationship to Contact models
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    avatar = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    reset_token = Column(String, nullable=True)

    contacts = relationship("Contact", back_populates="user")
