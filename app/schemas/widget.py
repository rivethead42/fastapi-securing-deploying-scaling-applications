from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.utils.sanitizer import sanitize_string

class WidgetBase(BaseModel):
    """Base widget schema"""
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    category: str

    def __init__(self, **data):
        # Sanitize input data
        for field in ["name", "description", "category"]:
            if field in data and data[field]:
                data[field] = sanitize_string(data[field])
        super().__init__(**data)

class WidgetCreate(WidgetBase):
    """Schema for creating a widget"""
    pass

class WidgetUpdate(WidgetBase):
    """Schema for updating a widget"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    category: Optional[str] = None

class Widget(WidgetBase):
    """Schema for a widget"""
    id: str = Field(alias="_id")
    owner: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True