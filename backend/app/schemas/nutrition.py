"""
Nutrition-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class NutritionTargetsCreate(BaseModel):
    user_id: int
    target_date: Optional[date] = None
    is_training_day: bool = False

class NutritionTargetsResponse(BaseModel):
    id: int
    user_id: int
    date: date
    calories_target: Optional[int]
    protein_target_g: Optional[int]
    carbs_target_g: Optional[int]
    fat_target_g: Optional[int]
    fiber_target_g: Optional[int]
    is_training_day: bool
    goal_type: Optional[str]
    tdee_kcal: Optional[int]

    class Config:
        from_attributes = True
