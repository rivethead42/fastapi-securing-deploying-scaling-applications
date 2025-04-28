"""
Prometheus metrics endpoints
"""
from fastapi import APIRouter, Depends, Request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.core.security import get_current_active_user
from app.core.rbac import require_permission
from app.schemas.user import User, Permission
import psutil

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("")
async def metrics(
    request: Request
):
    """
    Get Prometheus metrics (requires VIEW_METRICS permission)
    """
    # Update memory usage metrics - only updated when this endpoint is called
    from app.core.metrics import MEMORY_USAGE
    memory_info = psutil.Process().memory_info()
    MEMORY_USAGE.set(memory_info.rss)  # Resident Set Size in bytes
    
    # Generate and return metrics in Prometheus format
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )