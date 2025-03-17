from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path

from app.core.security import get_current_active_user
from app.core.rbac import require_permission
from app.models.widget import (
    create_widget, 
    get_widgets, 
    get_widget, 
    update_widget, 
    delete_widget,
    count_widgets
)
from app.schemas.user import User, Permission
from app.schemas.widget import Widget, WidgetCreate, WidgetUpdate

router = APIRouter()

@router.post(
    "/", 
    response_model=Widget,
    dependencies=[Depends(require_permission(Permission.CREATE_WIDGET))]
)
async def create_new_widget(
    widget: WidgetCreate, 
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new widget (requires CREATE_WIDGET permission)
    """
    return await create_widget(widget, current_user.id)

@router.get(
    "/", 
    response_model=List[Widget],
    dependencies=[Depends(require_permission(Permission.READ_WIDGET))]
)
async def read_widgets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve widgets with optional filtering (requires READ_WIDGET permission)
    """
    return await get_widgets(current_user.id, skip, limit, category)

@router.get(
    "/count",
    dependencies=[Depends(require_permission(Permission.READ_WIDGET))]
)
async def count_user_widgets(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Count user's widgets with optional filtering (requires READ_WIDGET permission)
    """
    count = await count_widgets(current_user.id, category)
    return {"count": count}

@router.get(
    "/{widget_id}", 
    response_model=Widget,
    dependencies=[Depends(require_permission(Permission.READ_WIDGET))]
)
async def read_widget(
    widget_id: str = Path(..., title="The ID of the widget to get"), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific widget by ID (requires READ_WIDGET permission)
    """
    widget = await get_widget(widget_id, current_user.id)
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Widget not found"
        )
    return widget

@router.put(
    "/{widget_id}", 
    response_model=Widget,
    dependencies=[Depends(require_permission(Permission.UPDATE_WIDGET))]
)
async def update_existing_widget(
    widget_update: WidgetUpdate,
    widget_id: str = Path(..., title="The ID of the widget to update"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a widget (requires UPDATE_WIDGET permission)
    """
    updated_widget = await update_widget(widget_id, current_user.id, widget_update)
    if not updated_widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Widget not found"
        )
    return updated_widget

@router.delete(
    "/{widget_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.DELETE_WIDGET))]
)
async def delete_existing_widget(
    widget_id: str = Path(..., title="The ID of the widget to delete"), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a widget (requires DELETE_WIDGET permission)
    """
    deleted = await delete_widget(widget_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Widget not found"
        )
    return None