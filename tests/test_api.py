"""
Integration tests for API routes.
"""
import pytest
from datetime import date
from unittest.mock import patch


class TestAuthenticationRoutes:
    """Test authentication-related API routes."""
    
    def test_signup_success(self, client):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        
        response = client.post("/api/signup", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert data["verified"] is False
    
    def test_signup_duplicate_email(self, client, test_user):
        """Test registration with existing email."""
        user_data = {
            "email": test_user.email,
            "password": "somepassword123"
        }
        
        response = client.post("/api/signup", json=user_data)
        
        assert response.status_code == 409
        assert "Email already registered" in response.json()["detail"]
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_unverified_user(self, client, db_session):
        """Test login with unverified user."""
        from src.crud import create_user
        from src.schemas import UserCreate
        
        # Create unverified user
        user_data = UserCreate(email="unverified@example.com", password="testpass123")
        user = create_user(db_session, user_data)
        # User is unverified by default
        
        login_data = {
            "username": user.email,
            "password": "testpass123"
        }
        
        response = client.post("/api/login", data=login_data)
        
        assert response.status_code == 401
        assert "Please verify your email address" in response.json()["detail"]
    
    def test_verify_email_success(self, client, db_session):
        """Test successful email verification."""
        from src.crud import create_user
        from src.schemas import UserCreate
        
        # Create user with verification token
        user_data = UserCreate(email="toverify@example.com", password="testpass123")
        user = create_user(db_session, user_data)
        token = user.verification_token
        
        response = client.get(f"/api/verifyemail/{token}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is True
        assert data["email"] == "toverify@example.com"
    
    def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token."""
        response = client.get("/api/verifyemail/invalid_token")
        
        assert response.status_code == 404
        assert "User not found or already verified" in response.json()["detail"]
    
    def test_resend_verification_email_success(self, client, db_session):
        """Test resending verification email."""
        from src.crud import create_user
        from src.schemas import UserCreate
        
        # Create unverified user
        user_data = UserCreate(email="resend@example.com", password="testpass123")
        user = create_user(db_session, user_data)
        
        response = client.post(f"/api/resend-verification-email/?email={user.email}")
        
        assert response.status_code == 200
        assert "Verification email resent" in response.json()["message"]
    
    def test_resend_verification_email_user_not_found(self, client):
        """Test resending verification email for non-existent user."""
        response = client.post("/api/resend-verification-email/?email=nonexistent@example.com")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_resend_verification_email_already_verified(self, client, test_user):
        """Test resending verification email for already verified user."""
        response = client.post(f"/api/resend-verification-email/?email={test_user.email}")
        
        assert response.status_code == 400
        assert "User already verified" in response.json()["detail"]


class TestPasswordResetRoutes:
    """Test password reset API routes."""
    
    def test_request_password_reset_success(self, client, test_user):
        """Test successful password reset request."""
        request_data = {"email": test_user.email}
        
        response = client.post("/api/password-reset/request", json=request_data)
        
        assert response.status_code == 200
        assert "password reset link has been sent" in response.json()["message"]
    
    def test_request_password_reset_user_not_found(self, client):
        """Test password reset request for non-existent user."""
        request_data = {"email": "nonexistent@example.com"}
        
        response = client.post("/api/password-reset/request", json=request_data)
        
        # Should return success message for security (don't reveal if user exists)
        assert response.status_code == 200
        assert "password reset link has been sent" in response.json()["message"]
    
    def test_confirm_password_reset_success(self, client, test_user, db_session):
        """Test successful password reset confirmation."""
        # Set a reset token
        reset_token = "test_reset_token_123"
        test_user.reset_token = reset_token
        db_session.commit()
        
        confirm_data = {
            "token": reset_token,
            "new_password": "newpassword123"
        }
        
        with patch('src.crud.redis_client'):
            response = client.post("/api/password-reset/confirm", json=confirm_data)
        
        assert response.status_code == 200
        assert "Password reset successfully" in response.json()["message"]
    
    def test_confirm_password_reset_invalid_token(self, client):
        """Test password reset confirmation with invalid token."""
        confirm_data = {
            "token": "invalid_token",
            "new_password": "newpassword123"
        }
        
        response = client.post("/api/password-reset/confirm", json=confirm_data)
        
        assert response.status_code == 400
        assert "Invalid or expired reset token" in response.json()["detail"]


class TestUserRoutes:
    """Test user management API routes."""
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/users/me/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert data["verified"] is True
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/users/me/")
        
        assert response.status_code == 401
    
    def test_update_avatar_admin_success(self, client, admin_auth_headers):
        """Test updating avatar as admin user."""
        # Mock file upload
        files = {"file": ("test_avatar.jpg", b"fake image data", "image/jpeg")}
        
        with patch('src.cloudinary_utils.upload_avatar') as mock_upload, \
             patch('src.redis_client.redis_client'):
            mock_upload.return_value = "https://example.com/avatar.jpg"
            
            response = client.patch("/api/users/avatar", files=files, headers=admin_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["avatar"] == "https://example.com/avatar.jpg"
    
    def test_update_avatar_regular_user_forbidden(self, client, auth_headers):
        """Test updating avatar as regular user (should be forbidden)."""
        files = {"file": ("test_avatar.jpg", b"fake image data", "image/jpeg")}
        
        response = client.patch("/api/users/avatar", files=files, headers=auth_headers)
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]


class TestContactRoutes:
    """Test contact management API routes."""
    
    def test_create_contact_success(self, client, auth_headers, test_contact_data):
        """Test successful contact creation."""
        response = client.post("/api/contacts/", json=test_contact_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == test_contact_data["first_name"]
        assert data["last_name"] == test_contact_data["last_name"]
        assert data["email"] == test_contact_data["email"]
        assert "id" in data
        assert "user_id" in data
    
    def test_create_contact_unauthorized(self, client, test_contact_data):
        """Test creating contact without authentication."""
        response = client.post("/api/contacts/", json=test_contact_data)
        
        assert response.status_code == 401
    
    def test_get_contacts_success(self, client, auth_headers, db_session, test_user):
        """Test getting all contacts for user."""
        # Create some test contacts first
        from src.crud import create_contact
        from src.schemas import ContactCreate
        
        for i in range(3):
            contact_data = ContactCreate(
                first_name=f"Contact{i}",
                last_name="Test",
                email=f"contact{i}@example.com",
                phone_number=f"+123456789{i}",
                birthday=date(1990, 1, 1)
            )
            create_contact(db_session, contact_data, test_user.id)
        
        response = client.get("/api/contacts/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("first_name" in contact for contact in data)
    
    def test_get_contacts_pagination(self, client, auth_headers, db_session, test_user):
        """Test getting contacts with pagination."""
        # Create 5 test contacts
        from src.crud import create_contact
        from src.schemas import ContactCreate
        
        for i in range(5):
            contact_data = ContactCreate(
                first_name=f"Contact{i}",
                last_name="Test",
                email=f"contact{i}@example.com",
                phone_number=f"+123456789{i}",
                birthday=date(1990, 1, 1)
            )
            create_contact(db_session, contact_data, test_user.id)
        
        # Test pagination
        response = client.get("/api/contacts/?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        response = client.get("/api/contacts/?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_get_contact_by_id_success(self, client, auth_headers, db_session, test_user):
        """Test getting specific contact by ID."""
        from src.crud import create_contact
        from src.schemas import ContactCreate
        
        contact_data = ContactCreate(
            first_name="Test",
            last_name="Contact",
            email="testcontact@example.com",
            phone_number="+1234567890",
            birthday=date(1990, 1, 1)
        )
        contact = create_contact(db_session, contact_data, test_user.id)
        
        response = client.get(f"/api/contacts/{contact.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == contact.id
        assert data["first_name"] == "Test"
        assert data["last_name"] == "Contact"
    
    def test_get_contact_by_id_not_found(self, client, auth_headers):
        """Test getting non-existent contact by ID."""
        response = client.get("/api/contacts/999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Contact not found" in response.json()["detail"]
    
    def test_update_contact_success(self, client, auth_headers, db_session, test_user):
        """Test successful contact update."""
        from src.crud import create_contact
        from src.schemas import ContactCreate
        
        # Create a contact first
        contact_data = ContactCreate(
            first_name="Original",
            last_name="Contact",
            email="original@example.com",
            phone_number="+1111111111",
            birthday=date(1990, 1, 1)
        )
        contact = create_contact(db_session, contact_data, test_user.id)
        
        # Update data
        update_data = {
            "first_name": "Updated",
            "last_name": "Contact",
            "email": "updated@example.com",
            "phone_number": "+2222222222",
            "birthday": "1990-01-01"
        }
        
        response = client.put(f"/api/contacts/{contact.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["email"] == "updated@example.com"
        assert data["phone_number"] == "+2222222222"
    
    def test_update_contact_not_found(self, client, auth_headers, test_contact_data):
        """Test updating non-existent contact."""
        response = client.put("/api/contacts/999", json=test_contact_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "Contact not found" in response.json()["detail"]
    
    def test_delete_contact_success(self, client, auth_headers, db_session, test_user):
        """Test successful contact deletion."""
        from src.crud import create_contact
        from src.schemas import ContactCreate
        
        # Create a contact first
        contact_data = ContactCreate(
            first_name="ToDelete",
            last_name="Contact",
            email="todelete@example.com",
            phone_number="+1111111111",
            birthday=date(1990, 1, 1)
        )
        contact = create_contact(db_session, contact_data, test_user.id)
        
        response = client.delete(f"/api/contacts/{contact.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == contact.id
        
        # Verify it's deleted
        get_response = client.get(f"/api/contacts/{contact.id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    def test_delete_contact_not_found(self, client, auth_headers):
        """Test deleting non-existent contact."""
        response = client.delete("/api/contacts/999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Contact not found" in response.json()["detail"]
    
    def test_search_contacts(self, client, auth_headers, db_session, test_user):
        """Test searching contacts."""
        from src.crud import create_contact
        from src.schemas import ContactCreate
        
        # Create test contacts
        contacts_data = [
            ("John", "Doe", "john.doe@example.com"),
            ("Jane", "Doe", "jane.doe@example.com"),
            ("Bob", "Smith", "bob.smith@example.com")
        ]
        
        for first, last, email in contacts_data:
            contact_data = ContactCreate(
                first_name=first,
                last_name=last,
                email=email,
                phone_number="+1111111111",
                birthday=date(1990, 1, 1)
            )
            create_contact(db_session, contact_data, test_user.id)
        
        # Search by first name
        response = client.get("/api/contacts/search?query=john", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "John"
        
        # Search by last name
        response = client.get("/api/contacts/search?query=doe", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_birthdays(self, client, auth_headers, db_session, test_user):
        """Test getting contacts with upcoming birthdays."""
        from src.crud import create_contact
        from src.schemas import ContactCreate
        from datetime import timedelta
        
        today = date.today()
        tomorrow = today + timedelta(days=1)
        far_future = today + timedelta(days=30)
        
        # Create contacts with different birthdays
        contacts_data = [
            ("Tomorrow", tomorrow),
            ("FarFuture", far_future)
        ]
        
        for name, birthday in contacts_data:
            contact_data = ContactCreate(
                first_name=name,
                last_name="Test",
                email=f"{name.lower()}@example.com",
                phone_number="+1111111111",
                birthday=birthday
            )
            create_contact(db_session, contact_data, test_user.id)
        
        response = client.get("/api/contacts/birthdays", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        # Should only return contacts with birthdays in next 7 days
        assert len(data) == 1
        assert data[0]["first_name"] == "Tomorrow"
    
    def test_contacts_unauthorized(self, client, test_contact_data):
        """Test accessing contacts without authentication."""
        # Test various endpoints without auth
        endpoints = [
            ("GET", "/api/contacts/"),
            ("POST", "/api/contacts/"),
            ("GET", "/api/contacts/1"),
            ("PUT", "/api/contacts/1"),
            ("DELETE", "/api/contacts/1"),
            ("GET", "/api/contacts/search?query=test"),
            ("GET", "/api/contacts/birthdays")
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=test_contact_data)
            elif method == "PUT":
                response = client.put(endpoint, json=test_contact_data)
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            assert response.status_code == 401