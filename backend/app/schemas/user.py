"""
User-related Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class GoalType(str, Enum):
    bulk = "bulk"
    cut = "cut"
    maintain = "maintain"
    recomp = "recomp"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    very_active = "very_active"
    athlete = "athlete"

class CookingSkill(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

# Request schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=13, le=120)
    sex: str = Field(..., pattern="^(male|female)$")
    height_inches: float = Field(..., gt=0, le=120)
    weight_lbs: float = Field(..., gt=0, le=1000)
    body_fat_pct: Optional[float] = Field(None, ge=1, le=60)
    goal_type: GoalType = GoalType.maintain
    activity_level: ActivityLevel = ActivityLevel.moderate
    training_days_per_week: int = Field(0, ge=0, le=7)
    weekly_budget_usd: float = Field(75.0, ge=0)
    dietary_restrictions: List[str] = []
    food_dislikes: List[str] = []
    cooking_skill: CookingSkill = CookingSkill.beginner
    available_equipment: List[str] = ["oven", "stovetop", "microwave"]

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    weight_lbs: Optional[float] = None
    body_fat_pct: Optional[float] = None
    goal_type: Optional[GoalType] = None
    activity_level: Optional[ActivityLevel] = None
    training_days_per_week: Optional[int] = None
    weekly_budget_usd: Optional[float] = None
    dietary_restrictions: Optional[List[str]] = None
    food_dislikes: Optional[List[str]] = None

# Response schemas
class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    sex: str
    height_inches: float
    weight_lbs: float
    body_fat_pct: Optional[float]
    muscle_mass_lbs: Optional[float]
    goal_type: str
    activity_level: str
    training_days_per_week: int
    cooking_skill: Optional[str]
    cooking_frequency: Optional[str]
    dietary_restrictions: List[str]
    food_dislikes: List[str]
    weekly_budget_usd: float
    available_equipment: List[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BodyMetricsCreate(BaseModel):
    weight_lbs: float = Field(..., gt=0)
    body_fat_pct: Optional[float] = Field(None, ge=1, le=60)
    measurement_date: Optional[date] = None
    waist_inches: Optional[float] = None
    chest_inches: Optional[float] = None
    arms_inches: Optional[float] = None
    legs_inches: Optional[float] = None
    notes: Optional[str] = None

class BodyMetricsResponse(BaseModel):
    id: int
    user_id: int
    date: date
    weight_lbs: float
    body_fat_pct: Optional[float]
    muscle_mass_lbs: Optional[float]
    waist_inches: Optional[float]
    chest_inches: Optional[float]
    arms_inches: Optional[float]
    legs_inches: Optional[float]
    notes: Optional[str]

    class Config:
        from_attributes = True

class ProgressSummary(BaseModel):
    status: str
    period_days: Optional[int] = None
    measurements_count: Optional[int] = None
    starting_weight: Optional[float] = None
    current_weight: Optional[float] = None
    weight_change_lbs: Optional[float] = None
    weight_change_pct: Optional[float] = None
    starting_bodyfat: Optional[float] = None
    current_bodyfat: Optional[float] = None
    bodyfat_change_pct: Optional[float] = None
    muscle_change_lbs: Optional[float] = None
    message: Optional[str] = None
