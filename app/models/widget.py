from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core.database import widgets_collection
from app.core.cache import get_cache, set_cache, delete_cache, get_cache_keys
from app.schemas.widget import Widget, WidgetCreate, WidgetUpdate
from app.core.config import settings

# Cache key templates
WIDGET_KEY = "widget:{}"
WIDGETS_BY_OWNER_KEY = "widgets:owner:{}"
WIDGETS_BY_CATEGORY_KEY = "widgets:owner:{}:category:{}"

async def create_widget(widget: WidgetCreate, owner_id: str) -> Widget:
    """Create a new widget"""
    widget_dict = widget.dict()
    widget_dict["_id"] = str(ObjectId())
    widget_dict["owner"] = owner_id
    widget_dict["created_at"] = datetime.utcnow()
    
    await widgets_collection.insert_one(widget_dict)
    
    # Invalidate cache for owner's widgets list
    owner_cache_key = WIDGETS_BY_OWNER_KEY.format(owner_id)
    await delete_cache(owner_cache_key)
    
    # Add to cache
    widget_obj = Widget(**widget_dict)
    widget_cache_key = WIDGET_KEY.format(widget_dict["_id"])
    await set_cache(widget_cache_key, widget_obj.dict(), settings.REDIS_TTL)
    
    return widget_obj

async def get_widgets(
    owner_id: str, 
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None
) -> List[Widget]:
    """Get widgets by owner with optional filtering"""
    # Try to get from cache first
    cache_key = WIDGETS_BY_OWNER_KEY.format(owner_id)
    if category:
        cache_key = WIDGETS_BY_CATEGORY_KEY.format(owner_id, category)
    
    # Add pagination to cache key
    cache_key = f"{cache_key}:skip:{skip}:limit:{limit}"
    
    cached_widgets = await get_cache(cache_key)
    if cached_widgets:
        return [Widget(**widget) for widget in cached_widgets]
    
    # If not in cache, query database
    query = {"owner": owner_id}
    if category:
        query["category"] = category
    
    cursor = widgets_collection.find(query).skip(skip).limit(limit)
    widgets = [Widget(**widget) async for widget in cursor]
    
    # Store in cache
    widgets_dict = [widget.dict() for widget in widgets]
    await set_cache(cache_key, widgets_dict, settings.REDIS_TTL)
    
    return widgets

async def get_widget(widget_id: str, owner_id: str) -> Optional[Widget]:
    """Get a widget by ID and owner"""
    # Try to get from cache first
    cache_key = WIDGET_KEY.format(widget_id)
    cached_widget = await get_cache(cache_key)
    if cached_widget:
        widget = Widget(**cached_widget)
        # Verify ownership
        if widget.owner == owner_id:
            return widget
    
    # If not in cache or wrong owner, query database
    widget = await widgets_collection.find_one({"_id": widget_id, "owner": owner_id})
    if widget:
        widget_obj = Widget(**widget)
        # Store in cache
        await set_cache(cache_key, widget_obj.dict(), settings.REDIS_TTL)
        return widget_obj
    return None

async def update_widget(
    widget_id: str, 
    owner_id: str, 
    widget_update: WidgetUpdate
) -> Optional[Widget]:
    """Update a widget"""
    # Filter out None values
    update_data = {k: v for k, v in widget_update.dict().items() if v is not None}
    if not update_data:
        # Nothing to update
        return await get_widget(widget_id, owner_id)
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update in database
    result = await widgets_collection.update_one(
        {"_id": widget_id, "owner": owner_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0 and result.matched_count == 0:
        return None
    
    # Update cache
    widget = await get_widget(widget_id, owner_id)
    
    # Invalidate list caches for this owner
    owner_cache_key = WIDGETS_BY_OWNER_KEY.format(owner_id)
    await delete_cache(owner_cache_key)
    
    # Also invalidate any category-specific caches
    if "category" in update_data:
        # We don't know all categories, so use a pattern
        pattern = f"widgets:owner:{owner_id}:category:*"
        keys = await get_cache_keys(pattern)
        for key in keys:
            await delete_cache(key)
    
    return widget

async def delete_widget(widget_id: str, owner_id: str) -> bool:
    """Delete a widget"""
    result = await widgets_collection.delete_one({"_id": widget_id, "owner": owner_id})
    
    if result.deleted_count > 0:
        # Delete from cache
        widget_cache_key = WIDGET_KEY.format(widget_id)
        await delete_cache(widget_cache_key)
        
        # Invalidate list caches
        owner_cache_key = WIDGETS_BY_OWNER_KEY.format(owner_id)
        await delete_cache(owner_cache_key)
        
        # Invalidate category caches
        pattern = f"widgets:owner:{owner_id}:category:*"
        keys = await get_cache_keys(pattern)
        for key in keys:
            await delete_cache(key)
        
        return True
    return False

async def count_widgets(owner_id: str, category: Optional[str] = None) -> int:
    """Count widgets by owner with optional filtering"""
    # Try to get from cache
    cache_key = f"count:widgets:owner:{owner_id}"
    if category:
        cache_key = f"{cache_key}:category:{category}"
    
    cached_count = await get_cache(cache_key)
    if cached_count is not None:
        return cached_count
    
    # Query database
    query = {"owner": owner_id}
    if category:
        query["category"] = category
    
    count = await widgets_collection.count_documents(query)
    
    # Cache result
    await set_cache(cache_key, count, settings.REDIS_TTL)
    
    return count