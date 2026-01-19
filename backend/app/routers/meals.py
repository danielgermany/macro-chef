"""
Meal tracking API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.schemas.meal import (
    MealLogCreate, MealLogResponse,
    DailyProgressResponse, WeeklySummaryResponse,
    MealRecommendationResponse
)
from app.services import MealTracker, MealRecommender

router = APIRouter()

def get_meal_tracker() -> MealTracker:
    return MealTracker()

def get_meal_recommender() -> MealRecommender:
    return MealRecommender()

@router.post("/log", response_model=MealLogResponse, status_code=201)
async def log_meal(
    meal_data: MealLogCreate,
    user_id: int = Query(..., description="User ID"),
    tracker: MealTracker = Depends(get_meal_tracker)
):
    """Log a meal with nutrition data."""
    try:
        meal_id = tracker.log_meal(
            user_id=user_id,
            meal_name=meal_data.meal_name,
            calories=meal_data.calories,
            protein_g=meal_data.protein_g,
            carbs_g=meal_data.carbs_g,
            fat_g=meal_data.fat_g,
            meal_time=meal_data.meal_time.value,
            fiber_g=meal_data.fiber_g,
            sugar_g=meal_data.sugar_g,
            saturated_fat_g=meal_data.saturated_fat_g,
            sodium_mg=meal_data.sodium_mg,
            cholesterol_mg=meal_data.cholesterol_mg,
            serving_size=meal_data.serving_size,
            notes=meal_data.notes,
            rating=meal_data.rating,
            meal_date=meal_data.meal_date,
            meal_template_id=meal_data.meal_template_id
        )
        # Return the logged meal
        history = tracker.get_meal_history(days=1, user_id=user_id)
        return history[0] if history else None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/progress", response_model=DailyProgressResponse)
async def get_daily_progress(
    user_id: int = Query(..., description="User ID"),
    target_date: Optional[date] = None,
    tracker: MealTracker = Depends(get_meal_tracker)
):
    """Get nutrition progress for a specific day."""
    return tracker.get_daily_progress(user_id=user_id, target_date=target_date)

@router.get("/history", response_model=List[MealLogResponse])
async def get_meal_history(
    user_id: int = Query(..., description="User ID"),
    days: Optional[int] = Query(None, ge=1, le=90),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    meal_name: Optional[str] = None,
    tracker: MealTracker = Depends(get_meal_tracker)
):
    """Get meal history with optional filtering by date range or meal name."""
    # If date range is provided, use it; otherwise use days
    if start_date and end_date:
        # Calculate days from date range
        delta = (end_date - start_date).days + 1
        days = min(delta, 90)  # Cap at 90 days
    elif not days:
        days = 7  # Default to 7 days
    
    history = tracker.get_meal_history(days=days, meal_name=meal_name, user_id=user_id)
    
    # Filter by date range if provided
    if start_date and end_date:
        filtered_history = [
            meal for meal in history
            if start_date <= date.fromisoformat(meal['meal_date']) <= end_date
        ]
        return filtered_history
    
    return history

@router.get("/weekly-summary", response_model=WeeklySummaryResponse)
async def get_weekly_summary(
    user_id: int = Query(..., description="User ID"),
    days: int = Query(7, ge=1, le=30),
    tracker: MealTracker = Depends(get_meal_tracker)
):
    """Get weekly nutrition summary."""
    return tracker.get_weekly_summary(user_id=user_id, days=days)

@router.delete("/{meal_id}")
async def delete_meal(
    meal_id: int,
    tracker: MealTracker = Depends(get_meal_tracker)
):
    """Delete a logged meal."""
    try:
        tracker.delete_meal(meal_id)
        return {"message": "Meal deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{meal_id}/rating")
async def update_meal_rating(
    meal_id: int,
    rating: int = Query(..., ge=1, le=5),
    tracker: MealTracker = Depends(get_meal_tracker)
):
    """Update meal rating."""
    try:
        tracker.update_meal_rating(meal_id, rating)
        return {"message": "Rating updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/recommendations", response_model=List[MealRecommendationResponse])
async def get_meal_recommendations(
    meal_time: str = Query("dinner", description="Meal time (breakfast, lunch, dinner, snack)"),
    user_id: int = Query(..., description="User ID"),
    max_time: Optional[int] = None,
    budget_limit: Optional[float] = None,
    allow_online_search: bool = True,
    recommender: MealRecommender = Depends(get_meal_recommender)
):
    """Get meal recommendations based on remaining macros and preferences."""
    try:
        recommendations = recommender.recommend_meal(
            meal_time=meal_time,
            user_id=user_id,
            max_time=max_time,
            budget_limit=budget_limit,
            allow_online_search=allow_online_search
        )
        return recommendations[:10]  # Limit to top 10
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
