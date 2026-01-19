"""
Nutrition targets API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date

from app.schemas.nutrition import NutritionTargetsCreate, NutritionTargetsResponse
from app.services import NutritionCalculator

router = APIRouter()

def get_nutrition_calc() -> NutritionCalculator:
    return NutritionCalculator()

@router.post("/targets", response_model=NutritionTargetsResponse, status_code=201)
async def generate_targets(
    target_data: NutritionTargetsCreate,
    calc: NutritionCalculator = Depends(get_nutrition_calc)
):
    """Generate daily nutrition targets for a user."""
    try:
        targets = calc.generate_daily_targets(
            user_id=target_data.user_id,
            target_date=target_data.target_date,
            is_training_day=target_data.is_training_day
        )
        if not targets:
            raise HTTPException(status_code=400, detail="Failed to generate targets")
        return targets
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/targets", response_model=NutritionTargetsResponse)
async def get_today_targets(
    user_id: int = Query(..., description="User ID"),
    calc: NutritionCalculator = Depends(get_nutrition_calc)
):
    """Get today's nutrition targets."""
    targets = calc.get_daily_targets(user_id=user_id, target_date=date.today())
    if not targets:
        raise HTTPException(status_code=404, detail="No targets found for today")
    return targets

@router.get("/targets/{target_date}", response_model=NutritionTargetsResponse)
async def get_targets_for_date(
    target_date: date,
    user_id: int = Query(..., description="User ID"),
    calc: NutritionCalculator = Depends(get_nutrition_calc)
):
    """Get nutrition targets for a specific date."""
    targets = calc.get_daily_targets(user_id=user_id, target_date=target_date)
    if not targets:
        raise HTTPException(status_code=404, detail=f"No targets found for {target_date}")
    return targets
