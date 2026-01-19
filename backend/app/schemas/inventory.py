"""
Inventory-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class InventoryItemCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    category: Optional[str] = None
    location: str = Field("pantry", pattern="^(fridge|freezer|pantry|counter)$")
    expiration_date: Optional[date] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = None

class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    expiration_date: Optional[date] = None
    notes: Optional[str] = None

class InventoryItemResponse(BaseModel):
    id: int
    user_id: int
    item_name: str
    quantity: float
    unit: str
    category: Optional[str]
    location: Optional[str]
    expiration_date: Optional[date]
    purchase_date: Optional[date]
    notes: Optional[str]

    class Config:
        from_attributes = True

class InventorySummaryResponse(BaseModel):
    total_items: int
    total_value_estimate: float
    expiring_soon: int
    by_category: dict
    by_location: dict
