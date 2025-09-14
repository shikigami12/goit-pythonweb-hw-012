"""
Pydantic schemas for request/response validation in the Contacts API.

This module defines all the data validation schemas used by the API
for serializing and deserializing data.
"""
from pydantic import BaseModel, EmailStr
from datetime import date
from .models import UserRole


class ContactBase(BaseModel):
    """Base schema for contact data validation."""
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_data: str | None = None


class ContactCreate(ContactBase):
    """Schema for creating a new contact."""
    pass


class Contact(ContactBase):
    """Schema for contact response data."""
    id: int
    user_id: int

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    """Base schema for user data validation."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class User(UserBase):
    """Schema for user response data."""
    id: int
    avatar: str | None = None
    verified: bool
    role: UserRole

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for JWT token data validation."""
    email: str | None = None


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str
