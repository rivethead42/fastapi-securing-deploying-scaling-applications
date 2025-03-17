from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Response

from app.core.security import get_current_active_user
from app.core.rbac import require_permission, has_permission
from app.models.user import (
    get_user_by_username, 
    get_user_by_email, 
    get_user_by_id,
    create_user, 
    update_user,
    update_user_role,
    update_user_status,
    add_user_permission,
    remove_user_permission,
    get_all_users,
    delete_user
)
from app.schemas.user import User, UserCreate, UserUpdate, Role, Permission

router = APIRouter()

@router.post("/", response_model=User)
async def register_user(user: UserCreate):
    """
    Register a new user
    """
    # Check if username is taken
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email is taken
    existing_email = await get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    return await create_user(user)

@router.put("/{user_id}", response_model=User)
async def update_user_details(
    user_update: UserUpdate,
    user_id: str = Path(..., title="The ID of the user to update"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a user's details
    
    This endpoint allows a user to update their own details
    or allows an admin to update any user's details.
    """
    # Check if user is updating their own profile or has update permission
    if current_user.id != user_id and not has_permission(current_user, Permission.UPDATE_USER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )
    
    try:
        updated_user = await update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/{user_id}/role", 
    response_model=User,
    dependencies=[Depends(require_permission(Permission.MANAGE_ROLES))]
)
async def update_role(
    role: Role,
    user_id: str = Path(..., title="The ID of the user to update")
):
    """
    Update a user's role (requires MANAGE_ROLES permission)
    """
    user = await update_user_role(user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return current_user

@router.get(
    "/", 
    response_model=List[User],
    dependencies=[Depends(require_permission(Permission.READ_USER))]
)
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all users (requires READ_USER permission)
    """
    return await get_all_users(skip, limit)

@router.get(
    "/{user_id}", 
    response_model=User,
    dependencies=[Depends(require_permission(Permission.READ_USER))]
)
async def read_user(user_id: str = Path(..., title="The ID of the user to get")):
    """
    Get a specific user by ID (requires READ_USER permission)
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put(
    "/{user_id}/role", 
    response_model=User,
    dependencies=[Depends(require_permission(Permission.MANAGE_ROLES))]
)
async def update_role(
    role: Role,
    user_id: str = Path(..., title="The ID of the user to update")
):
    """
    Update a user's role (requires MANAGE_ROLES permission)
    """
    user = await update_user_role(user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put(
    "/{user_id}/status",
    response_model=User,
    dependencies=[Depends(require_permission(Permission.MANAGE_ROLES))]
)
async def update_status(
    disabled: bool,
    user_id: str = Path(..., title="The ID of the user to update")
):
    """
    Enable or disable a user (requires MANAGE_ROLES permission)
    """
    # First update the status
    updated = await update_user_status(user_id, disabled)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Then get the updated user
    user = await get_user_by_id(user_id)
    return user

@router.post(
    "/{user_id}/permissions",
    response_model=User,
    dependencies=[Depends(require_permission(Permission.MANAGE_ROLES))]
)
async def add_permission(
    permission: Permission,
    user_id: str = Path(..., title="The ID of the user to update")
):
    """
    Add a permission to a user (requires MANAGE_ROLES permission)
    """
    user = await add_user_permission(user_id, permission)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete(
    "/{user_id}/permissions/{permission}",
    response_model=User,
    dependencies=[Depends(require_permission(Permission.MANAGE_ROLES))]
)
async def remove_permission(
    permission: Permission,
    user_id: str = Path(..., title="The ID of the user to update")
):
    """
    Remove a permission from a user (requires MANAGE_ROLES permission)
    """
    user = await remove_user_permission(user_id, permission)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.DELETE_USER))]
)
async def remove_user(
    user_id: str = Path(..., title="The ID of the user to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a user (requires DELETE_USER permission)
    
    This endpoint will delete a user and all their widgets.
    The last admin user cannot be deleted to ensure there's always
    at least one admin in the system.
    """
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    deleted = await delete_user(user_id)
    if not deleted:
        # Check if it was because of the last admin
        user = await get_user_by_id(user_id)
        if user and user.role == Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin user"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)