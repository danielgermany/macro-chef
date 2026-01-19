"""
Weekly meal plan Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date

class WeeklyPlanGenerate(BaseModel):
    week_start: Optional[date] = None
    plan_name: Optional[str] = None
    auto_recommend: bool = True

class WeeklyPlanResponse(BaseModel):
    plan_name: Optional[str]
    week_start: date
    week_end: date
    daily_plans: List[Dict]
    total_cost_estimate: float

class WeeklyPlanSave(BaseModel):
    plan: WeeklyPlanResponse

class ShoppingListResponse(BaseModel):
    items: List[Dict]
    total_estimated_cost: float
    grouped_by_category: Dict[str, List[Dict]]
    grouped_by_store: Optional[Dict[str, List[Dict]]] = None
