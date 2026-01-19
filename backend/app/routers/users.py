"""
User profile API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse,
    BodyMetricsCreate, BodyMetricsResponse, ProgressSummary
)
from app.services import UserProfileManager

router = APIRouter()

def get_user_manager() -> UserProfileManager:
    """Dependency to get UserProfileManager instance."""
    return UserProfileManager()

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Create a new user profile."""
    try:
        user_id = manager.create_user(
            name=user_data.name,
            age=user_data.age,
            sex=user_data.sex,
            height_inches=user_data.height_inches,
            weight_lbs=user_data.weight_lbs,
            body_fat_pct=user_data.body_fat_pct,
            goal_type=user_data.goal_type.value,
            activity_level=user_data.activity_level.value,
            training_days_per_week=user_data.training_days_per_week,
            weekly_budget_usd=user_data.weekly_budget_usd,
            dietary_restrictions=user_data.dietary_restrictions,
            food_dislikes=user_data.food_dislikes,
            cooking_skill=user_data.cooking_skill.value,
            available_equipment=user_data.available_equipment
        )
        user = manager.get_user(user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Get user profile by ID."""
    user = manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Update user profile."""
    # Filter out None values
    update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Convert enums to values
    if 'goal_type' in update_data:
        update_data['goal_type'] = update_data['goal_type'].value
    if 'activity_level' in update_data:
        update_data['activity_level'] = update_data['activity_level'].value
    
    try:
        manager.update_user(user_id=user_id, **update_data)
        return manager.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}/metrics", response_model=BodyMetricsResponse, status_code=201)
async def log_body_metrics(
    user_id: int,
    metrics: BodyMetricsCreate,
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Log body metrics for a user."""
    try:
        metric_id = manager.log_body_metrics(
            user_id=user_id,
            weight_lbs=metrics.weight_lbs,
            body_fat_pct=metrics.body_fat_pct,
            measurement_date=metrics.measurement_date,
            waist_inches=metrics.waist_inches,
            chest_inches=metrics.chest_inches,
            arms_inches=metrics.arms_inches,
            legs_inches=metrics.legs_inches,
            notes=metrics.notes
        )
        return manager.get_latest_metrics(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/metrics", response_model=List[BodyMetricsResponse])
async def get_metrics_history(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Get body metrics history."""
    return manager.get_metrics_history(days=days, user_id=user_id)

@router.get("/{user_id}/progress", response_model=ProgressSummary)
async def get_progress_summary(
    user_id: int,
    days: int = Query(30, ge=7, le=365),
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Get progress summary over a time period."""
    return manager.get_progress_summary(user_id=user_id, days=days)
