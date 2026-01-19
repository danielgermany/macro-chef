"""
Budget tracking Pydantic schemas.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date

class BudgetSummaryResponse(BaseModel):
    period_start: date
    period_end: date
    total_spent: float
    budget_limit: float
    remaining: float
    percentage_used: float
    daily_average: float
    category_breakdown: Dict[str, float]
    trend: Optional[str] = None

class SpendingTrendResponse(BaseModel):
    period: str
    data_points: List[Dict]
    trend_direction: str
    average_change: Optional[float] = None
