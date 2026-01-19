"""
Online recipe search API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.schemas.recipe import RecipeSearchParams, RecipeSearchResponse
from app.services import MealRecommender

router = APIRouter()

def get_meal_recommender() -> MealRecommender:
    return MealRecommender()

@router.get("/search", response_model=List[RecipeSearchResponse])
async def search_recipes(
    query: str = Query(..., min_length=1, max_length=200, description="Search query"),
    max_results: int = Query(5, ge=1, le=20),
    max_calories: Optional[int] = Query(None, ge=100),
    min_protein: Optional[int] = Query(None, ge=0),
    max_ready_time: Optional[int] = Query(None, ge=1),
    user_id: int = Query(1, description="User ID"),
    recommender: MealRecommender = Depends(get_meal_recommender)
):
    """Search online recipes using Spoonacular API."""
    try:
        results = recommender.search_online_recipes(
            query=query,
            max_results=max_results,
            max_calories=max_calories,
            min_protein=min_protein,
            max_ready_time=max_ready_time,
            user_id=user_id
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{recipe_id}", response_model=dict)
async def get_recipe_details(
    recipe_id: int,
    recommender: MealRecommender = Depends(get_meal_recommender)
):
    """Get detailed recipe information by ID."""
    try:
        # This would need to be implemented in MealRecommender or SpoonacularAPI
        # For now, return a placeholder
        raise HTTPException(status_code=501, detail="Not yet implemented")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
