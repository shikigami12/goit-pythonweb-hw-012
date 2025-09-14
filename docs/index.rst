Welcome to Contacts API documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Contacts API is a FastAPI-based REST API application for managing contacts with user authentication,
Redis caching, role-based access control, and password reset functionality.

Features
--------

* User authentication with JWT tokens
* Contact management (CRUD operations)
* User roles (user/admin)
* Redis caching for improved performance
* Password reset mechanism
* Email verification
* File upload for user avatars
* Rate limiting
* Search and filter contacts
* Birthday reminders

API Documentation
-----------------

The API provides the following endpoints:

Authentication
~~~~~~~~~~~~~~
* ``POST /api/signup`` - Register new user
* ``POST /api/login`` - User login
* ``GET /api/verifyemail/{token}`` - Verify email address
* ``POST /api/resend-verification-email/`` - Resend verification email
* ``POST /api/password-reset/request`` - Request password reset
* ``POST /api/password-reset/confirm`` - Confirm password reset

User Management
~~~~~~~~~~~~~~~
* ``GET /api/users/me/`` - Get current user profile
* ``PATCH /api/users/avatar`` - Update user avatar (admin only)

Contact Management
~~~~~~~~~~~~~~~~~~
* ``POST /api/contacts/`` - Create new contact
* ``GET /api/contacts/`` - Get all contacts
* ``GET /api/contacts/{id}`` - Get specific contact
* ``PUT /api/contacts/{id}`` - Update contact
* ``DELETE /api/contacts/{id}`` - Delete contact
* ``GET /api/contacts/search`` - Search contacts
* ``GET /api/contacts/birthdays`` - Get upcoming birthdays

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`