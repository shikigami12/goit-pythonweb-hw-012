"""
Unit tests for CRUD operations.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import patch

from src import crud, models, schemas


class TestUserCRUD:
    """Test user CRUD operations."""
    
    def test_get_user_by_email(self, db_session):
        """Test getting user by email."""
        # Create a test user
        user_data = schemas.UserCreate(email="test@example.com", password="testpass")
        created_user = crud.create_user(db_session, user_data)
        
        # Test getting the user
        found_user = crud.get_user_by_email(db_session, "test@example.com")
        assert found_user is not None
        assert found_user.email == "test@example.com"
        assert found_user.id == created_user.id
    
    def test_get_user_by_email_not_found(self, db_session):
        """Test getting non-existent user by email."""
        user = crud.get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None
    
    def test_create_user(self, db_session):
        """Test creating a new user."""
        user_data = schemas.UserCreate(email="newuser@example.com", password="newpass123")
        user = crud.create_user(db_session, user_data)
        
        assert user.email == "newuser@example.com"
        assert user.hashed_password != "newpass123"  # Should be hashed
        assert user.verified is False
        assert user.verification_token is not None
        assert user.role == models.UserRole.user
    
    def test_update_verification_status(self, db_session, test_user):
        """Test updating user verification status."""
        # Initially not verified (we set it in fixture but let's reset)
        test_user.verified = False
        test_user.verification_token = "test_token"
        db_session.commit()
        
        updated_user = crud.update_verification_status(db_session, test_user)
        assert updated_user.verified is True
        assert updated_user.verification_token is None
    
    def test_set_verification_token(self, db_session, test_user):
        """Test setting new verification token."""
        old_token = test_user.verification_token
        updated_user = crud.set_verification_token(db_session, test_user)
        
        assert updated_user.verification_token != old_token
        assert updated_user.verification_token is not None
    
    def test_update_avatar(self, db_session, test_user):
        """Test updating user avatar."""
        new_avatar_url = "https://example.com/avatar.jpg"
        updated_user = crud.update_avatar(db_session, test_user, new_avatar_url)
        
        assert updated_user.avatar == new_avatar_url
    
    @patch('src.crud.redis_client')
    def test_create_password_reset_token(self, mock_redis, db_session, test_user):
        """Test creating password reset token."""
        token = crud.create_password_reset_token(db_session, test_user.email)
        
        assert token is not None
        assert test_user.reset_token == token
        mock_redis.cache_reset_token.assert_called_once()
    
    def test_create_password_reset_token_user_not_found(self, db_session):
        """Test creating password reset token for non-existent user."""
        with pytest.raises(ValueError, match="User not found"):
            crud.create_password_reset_token(db_session, "nonexistent@example.com")
    
    def test_create_password_reset_token_user_not_verified(self, db_session):
        """Test creating password reset token for unverified user."""
        user_data = schemas.UserCreate(email="unverified@example.com", password="pass123")
        user = crud.create_user(db_session, user_data)
        # User is not verified by default
        
        with pytest.raises(ValueError, match="User not verified"):
            crud.create_password_reset_token(db_session, user.email)
    
    @patch('src.crud.redis_client')
    def test_reset_password(self, mock_redis, db_session, test_user):
        """Test resetting password with token."""
        # Set a reset token first
        reset_token = "test_reset_token"
        test_user.reset_token = reset_token
        db_session.commit()
        
        old_password = test_user.hashed_password
        success = crud.reset_password(db_session, reset_token, "newpassword123")
        
        assert success is True
        assert test_user.hashed_password != old_password
        assert test_user.reset_token is None
        mock_redis.invalidate_reset_token.assert_called_once()
        mock_redis.invalidate_user_cache.assert_called_once()
    
    def test_reset_password_invalid_token(self, db_session):
        """Test resetting password with invalid token."""
        success = crud.reset_password(db_session, "invalid_token", "newpassword123")
        assert success is False


class TestContactCRUD:
    """Test contact CRUD operations."""
    
    def test_create_contact(self, db_session, test_user):
        """Test creating a new contact."""
        contact_data = schemas.ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="+1234567890",
            birthday=date(1990, 1, 1),
            additional_data="Test contact"
        )
        
        contact = crud.create_contact(db_session, contact_data, test_user.id)
        
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert contact.email == "john.doe@example.com"
        assert contact.user_id == test_user.id
    
    def test_get_contact(self, db_session, test_user):
        """Test getting a specific contact."""
        # Create a contact first
        contact_data = schemas.ContactCreate(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone_number="+1234567891",
            birthday=date(1985, 5, 15)
        )
        created_contact = crud.create_contact(db_session, contact_data, test_user.id)
        
        # Test getting the contact
        found_contact = crud.get_contact(db_session, created_contact.id, test_user.id)
        assert found_contact is not None
        assert found_contact.first_name == "Jane"
        assert found_contact.user_id == test_user.id
    
    def test_get_contact_not_found(self, db_session, test_user):
        """Test getting non-existent contact."""
        contact = crud.get_contact(db_session, 999, test_user.id)
        assert contact is None
    
    def test_get_contacts(self, db_session, test_user):
        """Test getting all contacts for a user."""
        # Create multiple contacts
        for i in range(3):
            contact_data = schemas.ContactCreate(
                first_name=f"Contact{i}",
                last_name="Test",
                email=f"contact{i}@example.com",
                phone_number=f"+123456789{i}",
                birthday=date(1990, 1, 1)
            )
            crud.create_contact(db_session, contact_data, test_user.id)
        
        contacts = crud.get_contacts(db_session, test_user.id)
        assert len(contacts) == 3
    
    def test_get_contacts_pagination(self, db_session, test_user):
        """Test getting contacts with pagination."""
        # Create 5 contacts
        for i in range(5):
            contact_data = schemas.ContactCreate(
                first_name=f"Contact{i}",
                last_name="Test",
                email=f"contact{i}@example.com",
                phone_number=f"+123456789{i}",
                birthday=date(1990, 1, 1)
            )
            crud.create_contact(db_session, contact_data, test_user.id)
        
        # Test pagination
        contacts_page1 = crud.get_contacts(db_session, test_user.id, skip=0, limit=2)
        contacts_page2 = crud.get_contacts(db_session, test_user.id, skip=2, limit=2)
        
        assert len(contacts_page1) == 2
        assert len(contacts_page2) == 2
        assert contacts_page1[0].id != contacts_page2[0].id
    
    def test_update_contact(self, db_session, test_user):
        """Test updating an existing contact."""
        # Create a contact
        contact_data = schemas.ContactCreate(
            first_name="Original",
            last_name="Name",
            email="original@example.com",
            phone_number="+1111111111",
            birthday=date(1990, 1, 1)
        )
        contact = crud.create_contact(db_session, contact_data, test_user.id)
        
        # Update the contact
        updated_data = schemas.ContactCreate(
            first_name="Updated",
            last_name="Name",
            email="updated@example.com",
            phone_number="+2222222222",
            birthday=date(1990, 1, 1)
        )
        
        updated_contact = crud.update_contact(db_session, contact.id, updated_data, test_user.id)
        
        assert updated_contact.first_name == "Updated"
        assert updated_contact.email == "updated@example.com"
        assert updated_contact.phone_number == "+2222222222"
    
    def test_update_contact_not_found(self, db_session, test_user):
        """Test updating non-existent contact."""
        contact_data = schemas.ContactCreate(
            first_name="Test",
            last_name="Test",
            email="test@example.com",
            phone_number="+1111111111",
            birthday=date(1990, 1, 1)
        )
        
        updated_contact = crud.update_contact(db_session, 999, contact_data, test_user.id)
        assert updated_contact is None
    
    def test_delete_contact(self, db_session, test_user):
        """Test deleting a contact."""
        # Create a contact
        contact_data = schemas.ContactCreate(
            first_name="ToDelete",
            last_name="Contact",
            email="todelete@example.com",
            phone_number="+1111111111",
            birthday=date(1990, 1, 1)
        )
        contact = crud.create_contact(db_session, contact_data, test_user.id)
        
        # Delete the contact
        deleted_contact = crud.delete_contact(db_session, contact.id, test_user.id)
        
        assert deleted_contact is not None
        assert deleted_contact.id == contact.id
        
        # Verify it's actually deleted
        found_contact = crud.get_contact(db_session, contact.id, test_user.id)
        assert found_contact is None
    
    def test_delete_contact_not_found(self, db_session, test_user):
        """Test deleting non-existent contact."""
        deleted_contact = crud.delete_contact(db_session, 999, test_user.id)
        assert deleted_contact is None
    
    def test_search_contacts(self, db_session, test_user):
        """Test searching contacts."""
        # Create test contacts
        contacts_data = [
            ("John", "Doe", "john.doe@example.com"),
            ("Jane", "Doe", "jane.doe@example.com"),
            ("Bob", "Smith", "bob.smith@example.com"),
            ("Alice", "Johnson", "alice.johnson@example.com")
        ]
        
        for first, last, email in contacts_data:
            contact_data = schemas.ContactCreate(
                first_name=first,
                last_name=last,
                email=email,
                phone_number="+1111111111",
                birthday=date(1990, 1, 1)
            )
            crud.create_contact(db_session, contact_data, test_user.id)
        
        # Test searching by first name (case insensitive search will find John and Johnson)
        results = crud.search_contacts(db_session, "john", test_user.id)
        assert len(results) == 2  # Finds both "John" and "Alice Johnson"
        first_names = [r.first_name for r in results]
        assert "John" in first_names
        
        # Test searching by last name
        results = crud.search_contacts(db_session, "doe", test_user.id)
        assert len(results) == 2
        
        # Test searching by email
        results = crud.search_contacts(db_session, "smith", test_user.id)
        assert len(results) == 1
        assert results[0].email == "bob.smith@example.com"
    
    def test_get_birthdays(self, db_session, test_user):
        """Test getting contacts with upcoming birthdays."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=6)
        far_future = today + timedelta(days=30)
        
        # Create contacts with different birthdays
        contacts_data = [
            ("Today", today),
            ("Tomorrow", tomorrow),
            ("NextWeek", next_week),
            ("FarFuture", far_future)
        ]
        
        for name, birthday in contacts_data:
            contact_data = schemas.ContactCreate(
                first_name=name,
                last_name="Test",
                email=f"{name.lower()}@example.com",
                phone_number="+1111111111",
                birthday=birthday
            )
            crud.create_contact(db_session, contact_data, test_user.id)
        
        # Get upcoming birthdays (within 7 days)
        upcoming_birthdays = crud.get_birthdays(db_session, test_user.id)
        
        # Should return 3 contacts (today, tomorrow, next week) but not far future
        assert len(upcoming_birthdays) == 3
        birthday_names = [contact.first_name for contact in upcoming_birthdays]
        assert "Today" in birthday_names
        assert "Tomorrow" in birthday_names
        assert "NextWeek" in birthday_names
        assert "FarFuture" not in birthday_names