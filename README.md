# FastAPI Widget API

A RESTful API for managing widgets with user authentication, built with FastAPI and MongoDB.

## Features

- **Authentication and Authorization**:
  - JWT-based authentication system
  - Secure password hashing with bcrypt
  - Role-based access control

- **Data Validation and Sanitization**:
  - Pydantic models for data validation
  - NH3 for input sanitization to prevent XSS attacks
  - Email validation

- **Widget CRUD Operations**:
  - Create, read, update, and delete endpoints for widgets
  - Query parameters for filtering and pagination
  - Owner-based authorization

- **MongoDB Integration**:
  - Async connection using motor
  - Document modeling with Pydantic
  - BSON ObjectId handling

## Project Structure

```
app/
├── api/             # API route definitions
├── core/            # Core functionality
├── models/          # Database models
├── schemas/         # Pydantic schemas
├── utils/           # Utility functions
├── tests/           # Test suite
```

## Installation

### Prerequisites

- Python 3.8+
- MongoDB

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fastapi-widget-api.git
   cd fastapi-widget-api
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

5. Start the application:
   ```
   uvicorn main:app --reload
   ```

## API Documentation

Once the application is running, you can access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication and Authorization

The API supports flexible authentication options and RBAC for authorization:

1. Register a new user:
   ```
   POST /users/
   ```

2. Get an access token (two methods available):
   
   Form data authentication (traditional OAuth2):
   ```
   POST /token
   Content-Type: application/x-www-form-urlencoded

   username=your_username&password=your_password
   ```
   
   JSON authentication (API-friendly):
   ```
   POST /token/json
   Content-Type: application/json

   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

3. Use the token in the Authorization header:
   ```
   Authorization: Bearer {your_token}
   ```

### Roles and Permissions

The API has three predefined roles:

- **Admin**: Full access to all features
- **Manager**: Can manage widgets and view users
- **User**: Can only manage their own widgets

To create an admin user, run the initialization script:
```
python app/scripts/init_admin.py
```

Users can update their own information:
```
PUT /users/{user_id}                 # Update user details (username, email, password)
```

Admin users can manage roles and permissions for other users:
```
PUT /users/{user_id}                 # Update any user's details
PUT /users/{user_id}/role            # Change a user's role
POST /users/{user_id}/permissions    # Add a permission
DELETE /users/{user_id}/permissions/{permission}  # Remove a permission
DELETE /users/{user_id}              # Delete a user
```

**Important Notes:** 
- The system prevents deleting the last admin user to ensure there's always at least one administrator account available.
- Regular users can only update their own information, while admin users can update any user.
- The username and email must be unique across all users.

## Security Features

- All text inputs are sanitized using NH3 to prevent XSS attacks
- Passwords are securely hashed with bcrypt
- JWT tokens expire after 30 minutes
- MongoDB connection is configurable via environment variables
- Authentication is required for all widget operations
- CORS (Cross-Origin Resource Sharing) protection
- Rate limiting to prevent abuse:
  - Different limits for anonymous vs. authenticated users
  - Configurable rate limit windows
  - Rate limit headers included in responses
- Role-Based Access Control (RBAC):
  - Three predefined roles: Admin, Manager, and User
  - Granular permission system
  - Role-based and user-specific permissions
  - Protected admin endpoints
  - Permission-based dependencies for route protection