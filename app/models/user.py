from bson import ObjectId
from typing import Optional, List
from app.core.database import users_collection
from app.core.security import get_password_hash, verify_password
from app.schemas.user import User, UserCreate, Role, Permission
from app.core.rbac import get_permissions_for_role

async def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username"""
    user = await users_collection.find_one({"username": username})
    if user:
        return User(**user)
    return None

async def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email"""
    user = await users_collection.find_one({"email": email})
    if user:
        return User(**user)
    return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by ID"""
    user = await users_collection.find_one({"_id": user_id})
    if user:
        return User(**user)
    return None

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password"""
    user_dict = await users_collection.find_one({"username": username})
    if not user_dict:
        return None
    if not verify_password(password, user_dict["password"]):
        return None
    return User(**user_dict)

async def create_user(user: UserCreate) -> User:
    """Create a new user"""
    # Create user dict with hashed password
    user_dict = user.dict()
    user_dict["password"] = get_password_hash(user_dict["password"])
    user_dict["_id"] = str(ObjectId())
    user_dict["disabled"] = False
    
    # Set default role and get corresponding permissions
    role = user_dict.get("role", Role.USER)
    permissions = get_permissions_for_role(role)
    user_dict["permissions"] = permissions
    
    # Insert into database
    await users_collection.insert_one(user_dict)
    
    # Return user without password
    return User(**user_dict)

async def update_user_status(user_id: str, disabled: bool) -> bool:
    """Update a user's disabled status"""
    result = await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"disabled": disabled}}
    )
    return result.modified_count > 0

async def update_user_role(user_id: str, role: Role) -> Optional[User]:
    """Update a user's role and permissions"""
    # Get permissions for the new role
    permissions = get_permissions_for_role(role)
    
    # Update the user in the database
    result = await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"role": role, "permissions": permissions}}
    )
    
    if result.modified_count > 0:
        return await get_user_by_id(user_id)
    return None

async def add_user_permission(user_id: str, permission: Permission) -> Optional[User]:
    """Add a specific permission to a user"""
    # First, get the user to check current permissions
    user = await get_user_by_id(user_id)
    if not user:
        return None
    
    # Add the permission if not already present
    current_permissions = user.permissions
    if permission not in current_permissions:
        current_permissions.append(permission)
        
        # Update the user in the database
        await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"permissions": current_permissions}}
        )
        
        return await get_user_by_id(user_id)
    
    return user

async def remove_user_permission(user_id: str, permission: Permission) -> Optional[User]:
    """Remove a specific permission from a user"""
    # First, get the user to check current permissions
    user = await get_user_by_id(user_id)
    if not user:
        return None
    
    # Remove the permission if present
    current_permissions = user.permissions
    if permission in current_permissions:
        current_permissions.remove(permission)
        
        # Update the user in the database
        await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"permissions": current_permissions}}
        )
        
        return await get_user_by_id(user_id)
    
    return user

async def get_all_users(skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users (for admin purposes)"""
    cursor = users_collection.find().skip(skip).limit(limit)
    return [User(**user) async for user in cursor]

async def update_user(user_id: str, user_update) -> Optional[User]:
    """Update a user's information"""
    # Check if user exists
    user = await get_user_by_id(user_id)
    if not user:
        return None
    
    # Create update data dictionary
    update_data = {}
    
    # Handle username update
    if user_update.username is not None and user_update.username != user.username:
        # Check if username is already taken
        existing_user = await get_user_by_username(user_update.username)
        if existing_user and existing_user.id != user_id:
            raise ValueError("Username already taken")
        update_data["username"] = user_update.username
    
    # Handle email update
    if user_update.email is not None and user_update.email != user.email:
        # Check if email is already taken
        existing_email = await get_user_by_email(user_update.email)
        if existing_email and existing_email.id != user_id:
            raise ValueError("Email already registered")
        update_data["email"] = user_update.email
    
    # Handle password update
    if user_update.password is not None:
        update_data["password"] = get_password_hash(user_update.password)
    
    # Update user if there are changes
    if update_data:
        result = await users_collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0 or result.matched_count > 0:
            # Return updated user
            return await get_user_by_id(user_id)
    else:
        # No changes, return original user
        return user
    
    return None

async def delete_user(user_id: str) -> bool:
    """Delete a user by ID"""
    # Don't allow deletion if it's the last admin user
    user = await get_user_by_id(user_id)
    if not user:
        return False
    
    # Check if this is the last admin
    if user.role == Role.ADMIN:
        # Count admin users
        admin_count = await users_collection.count_documents({"role": Role.ADMIN})
        if admin_count <= 1:
            # This is the last admin, don't allow deletion
            return False
    
    # Delete the user
    result = await users_collection.delete_one({"_id": user_id})
    
    # Also delete all widgets owned by this user
    from app.core.database import db
    await db.widgets.delete_many({"owner": user_id})
    
    return result.deleted_count > 0