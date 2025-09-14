# Contacts API - Final Homework Assignment

A comprehensive REST API application built with FastAPI for managing contacts with advanced features including user authentication, Redis caching, role-based access control, and password reset functionality.

## ✅ Assignment Completion Status

All required features have been implemented:

### 📚 Documentation (✅ Completed)
- ✅ Sphinx documentation with comprehensive docstrings
- ✅ All major functions and classes documented
- ✅ API endpoint documentation
- ✅ Generated HTML documentation in `docs/_build/html/`

### 🧪 Testing (✅ Completed - 98% Coverage!)
- ✅ Unit tests for repository modules (`tests/test_crud.py`, `tests/test_auth.py`)
- ✅ Integration tests for API routes (`tests/test_api.py`)
- ✅ Redis client testing (`tests/test_redis_client.py`)
- ✅ **98% test coverage** (exceeds required 75%)
- ✅ pytest-cov integration

### 🔄 Redis Caching (✅ Completed)
- ✅ Redis integration for user session caching
- ✅ `get_current_user` function optimized with Redis cache
- ✅ Automatic cache invalidation on user updates
- ✅ Password reset token caching

### 🔐 Password Reset (✅ Completed)
- ✅ Secure password reset token generation
- ✅ Email-based password reset flow
- ✅ Token validation and expiration
- ✅ Redis integration for token storage

### 👥 User Roles & Access Control (✅ Completed)
- ✅ User roles: `user` and `admin`
- ✅ Role-based access control decorators
- ✅ Admin-only avatar upload functionality
- ✅ Database schema with role enum

### 🐳 Containerization (✅ Completed)
- ✅ Updated Docker Compose with Redis service
- ✅ Environment variable configuration
- ✅ Service orchestration

## 🚀 Features

### Authentication & Authorization
- JWT token-based authentication
- Email verification system
- Password reset mechanism
- Role-based access control (user/admin)
- Secure password hashing with bcrypt

### Contact Management
- Full CRUD operations for contacts
- Search functionality (by name/email)
- Birthday reminders (upcoming 7 days)
- User-specific contact isolation

### Performance & Caching
- Redis caching for user sessions
- Optimized database queries
- Rate limiting protection

### File Upload
- Cloudinary integration for avatar uploads
- Admin-only avatar management

## 🛠️ Technology Stack

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Pydantic** - Data validation and serialization
- **JWT** - Authentication tokens
- **Cloudinary** - File storage service
- **Docker** - Containerization
- **Pytest** - Testing framework
- **Sphinx** - Documentation generation

## 📦 Installation & Setup

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd goit-pythonweb-hw-012
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:mysecretpassword@db:5432/contacts_db
REDIS_URL=redis://redis:6379
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

4. Start services:
```bash
docker-compose up -d
```

### Local Development

1. Install dependencies:
```bash
pipenv install --dev
pipenv shell
```

2. Set up environment variables in `.env`

3. Start PostgreSQL and Redis services

4. Run the application:
```bash
uvicorn src.main:app --reload
```

## 🧪 Running Tests

```bash
# Run all tests with coverage
pipenv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test categories
pipenv run pytest tests/test_crud.py -v
pipenv run pytest tests/test_api.py -v
pipenv run pytest tests/test_auth.py -v

# Generate coverage report
pipenv run pytest --cov=src --cov-report=html
# View coverage report at htmlcov/index.html
```

## 📖 API Documentation

### Authentication Endpoints
- `POST /api/signup` - Register new user
- `POST /api/login` - User login
- `GET /api/verifyemail/{token}` - Verify email
- `POST /api/resend-verification-email/` - Resend verification
- `POST /api/password-reset/request` - Request password reset
- `POST /api/password-reset/confirm` - Confirm password reset

### User Management
- `GET /api/users/me/` - Get current user profile
- `PATCH /api/users/avatar` - Update avatar (admin only)

### Contact Management
- `POST /api/contacts/` - Create contact
- `GET /api/contacts/` - List contacts (with pagination)
- `GET /api/contacts/{id}` - Get specific contact
- `PUT /api/contacts/{id}` - Update contact
- `DELETE /api/contacts/{id}` - Delete contact
- `GET /api/contacts/search?query=term` - Search contacts
- `GET /api/contacts/birthdays` - Get upcoming birthdays

## 📚 Documentation

Generate Sphinx documentation:
```bash
pipenv run sphinx-build -b html docs docs/_build/html
```

View documentation: Open `docs/_build/html/index.html` in your browser.

## 🏗️ Project Structure

```
goit-pythonweb-hw-012/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api.py               # API routes
│   ├── auth.py              # Authentication & authorization
│   ├── crud.py              # Database operations
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   ├── redis_client.py      # Redis integration
│   └── cloudinary_utils.py  # File upload utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_crud.py         # Unit tests for CRUD
│   ├── test_auth.py         # Unit tests for auth
│   ├── test_api.py          # Integration tests for API
│   ├── test_redis_client.py # Redis client tests
│   └── test_simple.py       # Simple functionality tests
├── docs/                    # Sphinx documentation
├── docker-compose.yml       # Service orchestration
├── Dockerfile              # Container configuration
├── Pipfile                 # Dependencies
├── pytest.ini             # Test configuration
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔍 Test Coverage Report

Current test coverage: **98.10%** ✅

```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
src\api.py                  104      0   100%
src\auth.py                  49      0   100%
src\cloudinary_utils.py       9      2    78%   32-33
src\crud.py                  81      0   100%
src\database.py              15      4    73%   28-32
src\main.py                  14      1    93%   28
src\models.py                29      0   100%
src\redis_client.py          31      0   100%
src\schemas.py               36      0   100%
-------------------------------------------------------
TOTAL                       368      7    98%
```

## 🚦 API Usage Examples

### Register and Login
```bash
# Register
curl -X POST "http://localhost:8000/api/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

### Create Contact
```bash
curl -X POST "http://localhost:8000/api/contacts/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1234567890",
    "birthday": "1990-01-01"
  }'
```

## 🎯 Assignment Requirements Checklist

- ✅ **Sphinx Documentation**: Comprehensive docstrings and generated HTML docs
- ✅ **Unit Testing**: Repository modules fully tested
- ✅ **Integration Testing**: All API routes tested with pytest  
- ✅ **75%+ Test Coverage**: Achieved 98% coverage with pytest-cov
- ✅ **Redis Caching**: User sessions cached, optimized `get_current_user`
- ✅ **Password Reset**: Secure token-based reset mechanism
- ✅ **User Roles**: Admin/user roles with access control
- ✅ **Docker Compose**: Updated with Redis service
- ✅ **Environment Configuration**: Secure .env setup

## 🔒 Security Features

- Secure password hashing (bcrypt)
- JWT token authentication
- Rate limiting protection
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy)
- Environment variable security
- CORS protection
- Role-based access control

## 📈 Performance Optimizations

- Redis caching for frequently accessed user data
- Database query optimization
- Efficient pagination
- Connection pooling
- Async/await patterns where applicable

---

**Assignment Status**: ✅ **COMPLETED** with all requirements fulfilled and exceeding expectations (98% test coverage vs. required 75%).