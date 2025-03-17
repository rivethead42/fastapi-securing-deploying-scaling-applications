#!/usr/bin/env python
"""
Script to create an initial admin user for the API.
Run this script after setting up the application to create
an admin user with all permissions.
"""
import asyncio
import sys
import os
from typing import Optional
import getpass

# Add parent directory to path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import users_collection
from app.models.user import get_user_by_username, create_user
from app.schemas.user import UserCreate, Role
from app.core.config import settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def create_admin_user(username: str, email: str, password: Optional[str] = None) -> bool:
    """Create an admin user with full permissions"""
    # Check if user already exists
    existing_user = await get_user_by_username(username)
    if existing_user:
        print(f"User '{username}' already exists.")
        return False
    
    # Get password if not provided
    if not password:
        password = getpass.getpass("Enter password for admin user: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("Passwords do not match.")
            return False
        
        if len(password) < 8:
            print("Password must be at least 8 characters.")
            return False
    
    # Create admin user
    user_create = UserCreate(
        username=username,
        email=email,
        password=password,
        role=Role.ADMIN
    )
    
    # Create the user
    admin_user = await create_user(user_create)
    
    print(f"Admin user '{admin_user.username}' created successfully.")
    return True


async def main():
    """Main function to create admin user"""
    print("==== Create Admin User ====")
    print(f"MongoDB URI: {settings.MONGO_URI}")
    print(f"Database: {settings.MONGO_DB_NAME}")
    print()
    
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    
    success = await create_admin_user(username, email)
    
    if success:
        print("\nAdmin user created successfully!")
        print("You can now log in with this user and manage the API.")
    else:
        print("\nFailed to create admin user.")
        print("Please check the error messages above and try again.")
    

if __name__ == "__main__":
    asyncio.run(main())