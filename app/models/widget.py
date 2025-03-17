from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core.database import widgets_collection
from app.schemas.widget import Widget, WidgetCreate, WidgetUpdate

async def create_widget(widget: WidgetCreate, owner_id: str) -> Widget:
    """Create a new widget"""
    widget_dict = widget.dict()
    widget_dict["_id"] = str(ObjectId())
    widget_dict["owner"] = owner_id
    widget_dict["created_at"] = datetime.utcnow()
    
    await widgets_collection.insert_one(widget_dict)
    return Widget(**widget_dict)

async def get_widgets(
    owner_id: str, 
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None
) -> List[Widget]:
    """Get widgets by owner with optional filtering"""
    query = {"owner": owner_id}
    if category:
        query["category"] = category
    
    cursor = widgets_collection.find(query).skip(skip).limit(limit)
    return [Widget(**widget) async for widget in cursor]

async def get_widget(widget_id: str, owner_id: str) -> Optional[Widget]:
    """Get a widget by ID and owner"""
    widget = await widgets_collection.find_one({"_id": widget_id, "owner": owner_id})
    if widget:
        return Widget(**widget)
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
    
    if result.modified_count == 0:
        return None
    
    return await get_widget(widget_id, owner_id)

async def delete_widget(widget_id: str, owner_id: str) -> bool:
    """Delete a widget"""
    result = await widgets_collection.delete_one({"_id": widget_id, "owner": owner_id})
    return result.deleted_count > 0

async def count_widgets(owner_id: str, category: Optional[str] = None) -> int:
    """Count widgets by owner with optional filtering"""
    query = {"owner": owner_id}
    if category:
        query["category"] = category
    
    return await widgets_collection.count_documents(query)