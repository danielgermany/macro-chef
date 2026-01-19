"""
Budget tracking API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date

from app.schemas.budget import BudgetSummaryResponse, SpendingTrendResponse
from app.services import BudgetTracker

router = APIRouter()

def get_budget_tracker() -> BudgetTracker:
    return BudgetTracker()

@router.get("/weekly", response_model=BudgetSummaryResponse)
async def get_weekly_summary(
    user_id: int = Query(..., description="User ID"),
    week_start: Optional[date] = None,
    tracker: BudgetTracker = Depends(get_budget_tracker)
):
    """Get weekly budget summary."""
    try:
        summary = tracker.get_weekly_summary(user_id=user_id, week_start=week_start)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/monthly", response_model=BudgetSummaryResponse)
async def get_monthly_summary(
    user_id: int = Query(..., description="User ID"),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020),
    tracker: BudgetTracker = Depends(get_budget_tracker)
):
    """Get monthly budget summary."""
    try:
        summary = tracker.get_monthly_summary(user_id=user_id, month=month, year=year)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trends", response_model=SpendingTrendResponse)
async def get_spending_trends(
    user_id: int = Query(..., description="User ID"),
    days: int = Query(30, ge=7, le=365),
    tracker: BudgetTracker = Depends(get_budget_tracker)
):
    """Get spending trends over time."""
    try:
        trends = tracker.get_spending_trends(user_id=user_id, days=days)
        return trends
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/categories", response_model=dict)
async def get_category_breakdown(
    user_id: int = Query(..., description="User ID"),
    days: int = Query(30, ge=1, le=365),
    tracker: BudgetTracker = Depends(get_budget_tracker)
):
    """Get spending breakdown by category."""
    try:
        breakdown = tracker.get_category_breakdown(user_id=user_id, days=days)
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
