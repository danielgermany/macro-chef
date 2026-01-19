"""
Meal-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class MealTime(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"

# Request schemas
class MealLogCreate(BaseModel):
    meal_name: str = Field(..., min_length=1, max_length=200)
    calories: int = Field(..., ge=0)
    protein_g: float = Field(..., ge=0)
    carbs_g: float = Field(..., ge=0)
    fat_g: float = Field(..., ge=0)
    meal_time: MealTime = MealTime.snack
    fiber_g: Optional[float] = None
    sugar_g: Optional[float] = None
    saturated_fat_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    cholesterol_mg: Optional[float] = None
    serving_size: Optional[str] = None
    notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    meal_date: Optional[date] = None
    meal_template_id: Optional[int] = None

# Response schemas
class MealLogResponse(BaseModel):
    id: int
    user_id: int
    date: date
    meal_time: str
    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: Optional[float]
    sugar_g: Optional[float]
    saturated_fat_g: Optional[float]
    sodium_mg: Optional[float]
    cholesterol_mg: Optional[float]
    serving_size: Optional[str]
    notes: Optional[str]
    rating: Optional[int]
    logged_at: Optional[datetime]

    class Config:
        from_attributes = True

class NutritionTotals(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    saturated_fat_g: float
    sodium_mg: float
    cholesterol_mg: float

class NutritionRemaining(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float

class NutritionPercentages(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float

class DailyProgressResponse(BaseModel):
    date: date
    meals: List[MealLogResponse]
    meal_count: int
    totals: NutritionTotals
    targets: dict
    remaining: NutritionRemaining
    percentages: NutritionPercentages

class WeeklySummaryResponse(BaseModel):
    status: str
    period_days: Optional[int] = None
    days_with_data: Optional[int] = None
    averages: Optional[dict] = None
    adherence: Optional[dict] = None
    daily_data: Optional[List[dict]] = None
    message: Optional[str] = None

# Meal template schemas
class MealTemplateResponse(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    description: Optional[str]
    meal_type: Optional[str]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    total_time_minutes: Optional[int]
    difficulty: Optional[str]
    servings: int
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: Optional[float]
    cost_estimate_usd: Optional[float]
    rating: Optional[int]
    times_made: Optional[int]
    last_made: Optional[date]
    tags: Optional[str]
    is_batch_friendly: Optional[bool]
    can_freeze: Optional[bool]
    recipe_instructions: Optional[str]
    recipe_source: Optional[str]

    class Config:
        from_attributes = True

class MealRecommendationResponse(BaseModel):
    id: Optional[int] = None
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    total_time_minutes: Optional[int]
    difficulty: Optional[str]
    cost_estimate_usd: Optional[float]
    recommendation_score: float
    match_reasons: List[str]
    is_online_recipe: bool = False
    api_recipe_id: Optional[str] = None
    nutrition_validated: Optional[bool] = None
