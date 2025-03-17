from typing import List, Dict, Set
from fastapi import Depends, HTTPException, status
from app.schemas.user import User, Role, Permission
from app.core.security import get_current_active_user

# Role-based permission mappings
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.ADMIN: [
        # Admin has all permissions
        Permission.CREATE_WIDGET,
        Permission.READ_WIDGET,
        Permission.UPDATE_WIDGET,
        Permission.DELETE_WIDGET,
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.MANAGE_ROLES,
        Permission.VIEW_METRICS
    ],
    Role.MANAGER: [
        # Manager can perform widget operations and view users
        Permission.CREATE_WIDGET,
        Permission.READ_WIDGET,
        Permission.UPDATE_WIDGET,
        Permission.DELETE_WIDGET,
        Permission.READ_USER,
        Permission.VIEW_METRICS
    ],
    Role.USER: [
        # Regular user can only perform widget operations
        Permission.READ_WIDGET
    ]
}

def get_permissions_for_role(role: Role) -> List[Permission]:
    """Get the list of permissions for a given role"""
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(user: User, required_permission: Permission) -> bool:
    """Check if a user has a specific permission"""
    # Get all permissions based on role
    role_permissions = get_permissions_for_role(user.role) if user.role else []
    
    # Combine role permissions with any additional user-specific permissions
    all_permissions = set(role_permissions + user.permissions)
    
    return required_permission in all_permissions

async def get_current_user_with_permission(
    required_permission: Permission,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to check if the current user has the required permission.
    If not, raise a 403 Forbidden exception.
    """
    if not has_permission(current_user, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions to perform this action"
        )
    return current_user

# Factory function to create permission-based dependencies
def require_permission(permission: Permission):
    """
    Factory function that creates a dependency to check for a specific permission.
    
    Usage:
    @router.get("/widgets/", dependencies=[Depends(require_permission(Permission.READ_WIDGET))])
    async def read_widgets():
        # This endpoint requires READ_WIDGET permission
        ...
    """
    async def permission_dependency(current_user: User = Depends(get_current_active_user)):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions to perform this action"
            )
        return current_user
    
    return permission_dependency