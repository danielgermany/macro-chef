"""
Inventory management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    InventorySummaryResponse
)
from app.services import InventoryManager

router = APIRouter()

def get_inventory_manager() -> InventoryManager:
    return InventoryManager()

@router.get("/", response_model=List[InventoryItemResponse])
async def list_inventory(
    user_id: int = Query(..., description="User ID"),
    location: Optional[str] = None,
    category: Optional[str] = None,
    manager: InventoryManager = Depends(get_inventory_manager)
):
    """List all inventory items, optionally filtered by location or category."""
    return manager.get_all_items(user_id=user_id, location=location, category=category)

@router.post("/", response_model=InventoryItemResponse, status_code=201)
async def add_item(
    item_data: InventoryItemCreate,
    user_id: int = Query(..., description="User ID"),
    manager: InventoryManager = Depends(get_inventory_manager)
):
    """Add item to inventory."""
    try:
        item_id = manager.add_item(
            item_name=item_data.item_name,
            quantity=item_data.quantity,
            unit=item_data.unit,
            category=item_data.category,
            location=item_data.location,
            expiration_date=item_data.expiration_date,
            purchase_date=item_data.purchase_date,
            notes=item_data.notes,
            user_id=user_id
        )
        return manager.get_item(item_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_item(
    item_id: int,
    manager: InventoryManager = Depends(get_inventory_manager)
):
    """Get single inventory item by ID."""
    item = manager.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.patch("/{item_id}", response_model=InventoryItemResponse)
async def update_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    manager: InventoryManager = Depends(get_inventory_manager)
):
    """Update inventory item."""
    # Filter out None values
    update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    try:
        manager.update_item(item_id=item_id, **update_data)
        return manager.get_item(item_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    manager: InventoryManager = Depends(get_inventory_manager)
):
    """Delete inventory item."""
    try:
        manager.delete_item(item_id)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{item_id}/use")
async def use_item(
    item_id: int,
    quantity: float = Query(..., gt=0, description="Quantity to use"),
    manager: InventoryManager = Depends(get_inventory_manager)
):
    """Use item (reduce quantity)."""
    try:
        manager.use_item(item_id=item_id, quantity=quantity)
        return {"message": "Item quantity updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/expiring", response_model=List[InventoryItemResponse])
async def get_expiring_items(
    user_id: int = Query(..., description="User ID"),
    days: int = Query(7, ge=1, le=30, description="Days until expiration"),
    manager: InventoryManager = Depends(get_inventory_manager)
):
    """Get items expiring within specified days."""
    return manager.get_expiring_items(user_id=user_id, days=days)

@router.get("/summary", response_model=InventorySummaryResponse)
async def get_inventory_summary(
    user_id: int = Query(..., description="User ID"),
    manager: InventoryManager = Depends(get_inventory_manager)
):
    """Get inventory summary statistics."""
    return manager.get_inventory_summary(user_id=user_id)
