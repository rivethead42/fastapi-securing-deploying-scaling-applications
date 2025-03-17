from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_active_user
from app.core.rbac import require_permission
from app.schemas.user import User, Permission
from app.core.database import db

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get(
    "/metrics", 
    dependencies=[Depends(require_permission(Permission.VIEW_METRICS))]
)
async def get_metrics(current_user: User = Depends(get_current_active_user)):
    """
    Get system metrics (requires VIEW_METRICS permission)
    """
    # Count users
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"disabled": False})
    
    # Count widgets
    total_widgets = await db.widgets.count_documents({})
    
    # Get widget categories
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    categories = []
    async for category in db.widgets.aggregate(pipeline):
        categories.append({
            "category": category["_id"],
            "count": category["count"]
        })
    
    # Return metrics
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "widgets": {
            "total": total_widgets,
            "by_category": categories
        }
    }

@router.get(
    "/system-health",
    dependencies=[Depends(require_permission(Permission.VIEW_METRICS))]
)
async def get_system_health(current_user: User = Depends(get_current_active_user)):
    """
    Get system health information (requires VIEW_METRICS permission)
    """
    # Check database connection
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Return health info
    return {
        "database": {
            "status": db_status,
            "name": db.name
        },
        "api": {
            "status": "running"
        }
    }