"""
Weekly meal planning API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.schemas.plan import (
    WeeklyPlanGenerate, WeeklyPlanResponse, WeeklyPlanSave, ShoppingListResponse
)
from app.services import WeeklyPlanner, ShoppingListGenerator

router = APIRouter()

def get_weekly_planner() -> WeeklyPlanner:
    return WeeklyPlanner()

def get_shopping_list_gen() -> ShoppingListGenerator:
    return ShoppingListGenerator()

@router.post("/generate", response_model=WeeklyPlanResponse)
async def generate_plan(
    plan_data: WeeklyPlanGenerate,
    user_id: int = Query(..., description="User ID"),
    planner: WeeklyPlanner = Depends(get_weekly_planner)
):
    """Generate a weekly meal plan."""
    try:
        plan = planner.generate_weekly_plan(
            week_start=plan_data.week_start,
            user_id=user_id,
            plan_name=plan_data.plan_name,
            auto_recommend=plan_data.auto_recommend
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=dict, status_code=201)
async def save_plan(
    plan_data: WeeklyPlanSave,
    user_id: int = Query(..., description="User ID"),
    planner: WeeklyPlanner = Depends(get_weekly_planner)
):
    """Save a weekly meal plan."""
    try:
        plan_id = planner.save_plan(plan=plan_data.plan.model_dump(), user_id=user_id)
        return {"plan_id": plan_id, "message": "Plan saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[dict])
async def list_plans(
    user_id: int = Query(..., description="User ID"),
    limit: int = Query(10, ge=1, le=50),
    planner: WeeklyPlanner = Depends(get_weekly_planner)
):
    """List recent meal plans."""
    return planner.get_recent_plans(user_id=user_id, limit=limit)

@router.get("/{plan_id}", response_model=WeeklyPlanResponse)
async def get_plan(
    plan_id: int,
    planner: WeeklyPlanner = Depends(get_weekly_planner)
):
    """Get specific meal plan by ID."""
    plan = planner.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.get("/{plan_id}/shopping-list", response_model=ShoppingListResponse)
async def get_shopping_list(
    plan_id: int,
    shopping_gen: ShoppingListGenerator = Depends(get_shopping_list_gen)
):
    """Generate shopping list from meal plan."""
    try:
        shopping_list = shopping_gen.generate_from_plan(plan_id=plan_id)
        return shopping_list
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
