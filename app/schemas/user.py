from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from app.utils.sanitizer import sanitize_string

class Role(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class Permission(str, Enum):
    """Permissions for RBAC"""
    # Widget permissions
    CREATE_WIDGET = "create:widget"
    READ_WIDGET = "read:widget"
    UPDATE_WIDGET = "update:widget"
    DELETE_WIDGET = "delete:widget"
    
    # User permissions
    CREATE_USER = "create:user"
    READ_USER = "read:user"
    UPDATE_USER = "update:user"
    DELETE_USER = "delete:user"
    
    # Admin permissions
    MANAGE_ROLES = "manage:roles"
    VIEW_METRICS = "view:metrics"

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str

    def __init__(self, **data):
        # Sanitize input data
        if "username" in data:
            data["username"] = sanitize_string(data["username"])
        super().__init__(**data)

class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str
    role: Role = Role.USER  # Default role for new users

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
    def __init__(self, **data):
        # Sanitize input data
        if "username" in data and data["username"]:
            data["username"] = sanitize_string(data["username"])
        super().__init__(**data)

class User(UserBase):
    """Schema for a user"""
    id: str = Field(alias="_id")
    role: Role = Role.USER
    permissions: List[Permission] = []
    disabled: bool = False

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True  # Store enum values as strings