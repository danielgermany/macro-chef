# Macro Chef: Web Migration Plan
## Tkinter → FastAPI + React

---

## Executive Summary

This document outlines a phased migration strategy to transform Macro Chef from a Tkinter desktop application to a modern web application using FastAPI (backend) and React (frontend). The migration preserves your existing business logic while adding scalability, multi-user support, and a responsive UI.

**Estimated Timeline:** 4-6 weeks (part-time) or 2-3 weeks (full-time)

**Key Principles:**
- Preserve existing Python business logic (scripts/)
- Incremental migration (can run old + new simultaneously)
- Feature parity first, then enhancements

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure](#2-project-structure)
3. [Phase 1: Backend Foundation](#phase-1-backend-foundation-week-1)
4. [Phase 2: Core API Endpoints](#phase-2-core-api-endpoints-week-2)
5. [Phase 3: React Frontend Setup](#phase-3-react-frontend-setup-week-3)
6. [Phase 4: Frontend Feature Implementation](#phase-4-frontend-feature-implementation-week-3-4)
7. [Phase 5: Authentication & Multi-User](#phase-5-authentication--multi-user-week-4)
8. [Phase 6: Testing & Deployment](#phase-6-testing--deployment-week-5)
9. [Database Migration Strategy](#database-migration-strategy)
10. [API Specification](#api-specification)
11. [Component Mapping](#component-mapping)
12. [Tech Stack Details](#tech-stack-details)

---

## 1. Architecture Overview

### Current Architecture (Tkinter)
```
┌─────────────────────────────────────────────────────┐
│                   gui_app.py                        │
│              (Tkinter GUI Layer)                    │
└──────────────────────┬──────────────────────────────┘
                       │ Direct Python calls
┌──────────────────────▼──────────────────────────────┐
│                  scripts/                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │UserProfile  │ │MealTracker  │ │Inventory    │   │
│  │Manager      │ │             │ │Manager      │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │Nutrition    │ │Weekly       │ │Budget       │   │
│  │Calculator   │ │Planner      │ │Tracker      │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              SQLite Database                        │
│           (meal_planner.db)                         │
└─────────────────────────────────────────────────────┘
```

### Target Architecture (FastAPI + React)
```
┌─────────────────────────────────────────────────────┐
│                  React Frontend                     │
│    (Vite + TypeScript + TailwindCSS + Shadcn/ui)   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │Dashboard│ │Meals    │ │Inventory│ │Budget   │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/REST API (JSON)
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend                        │
│  ┌─────────────────────────────────────────────┐   │
│  │              API Routers                     │   │
│  │  /api/users  /api/meals  /api/inventory     │   │
│  │  /api/nutrition  /api/plans  /api/budget    │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │         Pydantic Schemas (DTOs)             │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │      Existing scripts/ (minimal changes)    │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│    PostgreSQL (Production) / SQLite (Dev)          │
└─────────────────────────────────────────────────────┘
```

---

## 2. Project Structure

### New Directory Structure
```
macro-chef/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings & environment
│   │   ├── database.py          # Database connection
│   │   │
│   │   ├── routers/             # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── users.py
│   │   │   ├── meals.py
│   │   │   ├── nutrition.py
│   │   │   ├── inventory.py
│   │   │   ├── plans.py
│   │   │   ├── budget.py
│   │   │   └── recipes.py       # Online recipe search
│   │   │
│   │   ├── schemas/             # Pydantic models (request/response)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── meal.py
│   │   │   ├── nutrition.py
│   │   │   ├── inventory.py
│   │   │   ├── plan.py
│   │   │   └── budget.py
│   │   │
│   │   ├── services/            # Business logic (your existing scripts)
│   │   │   ├── __init__.py
│   │   │   └── ... (symlink or copy from scripts/)
│   │   │
│   │   └── auth/                # Authentication (Phase 5)
│   │       ├── __init__.py
│   │       ├── jwt.py
│   │       └── dependencies.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_users.py
│   │   ├── test_meals.py
│   │   └── ...
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/                 # Database migrations
│       └── ...
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   │
│   │   ├── components/          # Reusable UI components
│   │   │   ├── ui/              # Shadcn/ui components
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── dashboard/
│   │   │   ├── meals/
│   │   │   ├── inventory/
│   │   │   └── ...
│   │   │
│   │   ├── pages/               # Route pages
│   │   │   ├── Dashboard.tsx
│   │   │   ├── MealTracker.tsx
│   │   │   ├── Nutrition.tsx
│   │   │   ├── Inventory.tsx
│   │   │   ├── WeeklyPlanner.tsx
│   │   │   └── Budget.tsx
│   │   │
│   │   ├── hooks/               # Custom React hooks
│   │   │   ├── useUser.ts
│   │   │   ├── useMeals.ts
│   │   │   └── ...
│   │   │
│   │   ├── services/            # API client functions
│   │   │   ├── api.ts           # Axios/fetch setup
│   │   │   ├── userService.ts
│   │   │   ├── mealService.ts
│   │   │   └── ...
│   │   │
│   │   ├── types/               # TypeScript types
│   │   │   ├── user.ts
│   │   │   ├── meal.ts
│   │   │   └── ...
│   │   │
│   │   └── lib/                 # Utilities
│   │       └── utils.ts
│   │
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── scripts/                     # KEEP - Your existing business logic
├── config/                      # KEEP - Existing config
├── database/                    # KEEP - SQLite for dev
├── docker-compose.yml           # Full stack orchestration
└── README.md
```

---

## Phase 1: Backend Foundation (Week 1)

### Goals
- Set up FastAPI project structure
- Create database connection layer
- Implement basic health check endpoint
- Configure CORS for frontend

### Tasks

#### 1.1 Create Backend Directory & Virtual Environment
```bash
cd D:\Projects\macro-chef
mkdir -p backend/app/routers backend/app/schemas backend/app/services backend/tests
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
pip freeze > requirements.txt
```

#### 1.2 Create Main FastAPI App

**File: `backend/app/main.py`**
```python
"""
Macro Chef API - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import users, meals, nutrition, inventory, plans, budget, recipes

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Cleanup

app = FastAPI(
    title="Macro Chef API",
    description="Meal planning and nutrition tracking API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(meals.router, prefix="/api/meals", tags=["meals"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["nutrition"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(plans.router, prefix="/api/plans", tags=["plans"])
app.include_router(budget.router, prefix="/api/budget", tags=["budget"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])

@app.get("/")
async def root():
    return {"message": "Welcome to Macro Chef API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

#### 1.3 Create Configuration

**File: `backend/app/config.py`**
```python
"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./database/meal_planner.db"
    
    # API Keys (from existing .env)
    SPOONACULAR_API_KEY: str = ""
    USDA_API_KEY: str = ""
    
    # Security (Phase 5)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

#### 1.4 Create Database Connection

**File: `backend/app/database.py`**
```python
"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 1.5 Link Existing Scripts as Services

Create a symlink or copy your existing scripts to be used as services:

**Option A: Symlink (Recommended for development)**
```bash
# From backend/app/services/
mklink /D services ..\..\scripts  # Windows
# ln -s ../../scripts services  # Linux/Mac
```

**Option B: Import path adjustment**

**File: `backend/app/services/__init__.py`**
```python
"""
Service layer - imports existing business logic from scripts/
"""
import sys
from pathlib import Path

# Add scripts directory to path
scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

# Re-export managers
from user_profile import UserProfileManager
from nutrition_calculator import NutritionCalculator
from meal_tracker import MealTracker
from meal_recommender import MealRecommender
from inventory_manager import InventoryManager
from weekly_planner import WeeklyPlanner
from budget_tracker import BudgetTracker
from shopping_list import ShoppingListGenerator
from spoonacular_api import SpoonacularAPI
from usda_api import USDAAPI
```

#### 1.6 Run the Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to see the auto-generated API documentation.

---

## Phase 2: Core API Endpoints (Week 2)

### Goals
- Implement all CRUD endpoints
- Create Pydantic schemas for validation
- Wrap existing managers with FastAPI routers

### 2.1 Pydantic Schemas

**File: `backend/app/schemas/user.py`**
```python
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
    cooking_skill: str
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
```

**File: `backend/app/schemas/meal.py`**
```python
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
    user_id: int
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
```

### 2.2 API Routers

**File: `backend/app/routers/users.py`**
```python
"""
User profile API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse,
    BodyMetricsCreate, BodyMetricsResponse, ProgressSummary
)
from app.services import UserProfileManager

router = APIRouter()

def get_user_manager(db: Session = Depends(get_db)) -> UserProfileManager:
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
```

**File: `backend/app/routers/meals.py`**
```python
"""
Meal tracking API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.database import get_db
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
    days: int = Query(7, ge=1, le=90),
    meal_name: Optional[str] = None,
    tracker: MealTracker = Depends(get_meal_tracker)
):
    """Get meal history."""
    return tracker.get_meal_history(days=days, meal_name=meal_name, user_id=user_id)

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
```

### 2.3 Remaining Routers (Create Similar Pattern)

Create these additional router files following the same pattern:

- **`backend/app/routers/nutrition.py`** - Wraps `NutritionCalculator`
  - `POST /targets` - Generate daily targets
  - `GET /targets` - Get daily targets
  - `GET /targets/{date}` - Get targets for specific date

- **`backend/app/routers/inventory.py`** - Wraps `InventoryManager`
  - `GET /` - List all items
  - `POST /` - Add item
  - `GET /{item_id}` - Get single item
  - `PATCH /{item_id}` - Update item
  - `DELETE /{item_id}` - Delete item
  - `POST /{item_id}/use` - Use item (reduce quantity)
  - `GET /expiring` - Get expiring items
  - `GET /summary` - Get inventory summary

- **`backend/app/routers/plans.py`** - Wraps `WeeklyPlanner`
  - `POST /generate` - Generate weekly plan
  - `POST /` - Save plan
  - `GET /` - List recent plans
  - `GET /{plan_id}` - Get specific plan
  - `GET /{plan_id}/shopping-list` - Generate shopping list

- **`backend/app/routers/budget.py`** - Wraps `BudgetTracker`
  - `GET /weekly` - Weekly summary
  - `GET /monthly` - Monthly summary
  - `GET /trends` - Spending trends
  - `GET /categories` - Category breakdown

- **`backend/app/routers/recipes.py`** - Wraps `SpoonacularAPI`
  - `GET /search` - Search online recipes
  - `GET /{recipe_id}` - Get recipe details

---

## Phase 3: React Frontend Setup (Week 3)

### Goals
- Initialize React project with Vite
- Configure TypeScript, TailwindCSS, and Shadcn/ui
- Create basic layout and routing

### Tasks

#### 3.1 Create React Project
```bash
cd D:\Projects\macro-chef
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

#### 3.2 Install Dependencies
```bash
# Core dependencies
npm install axios react-router-dom @tanstack/react-query zustand

# UI dependencies
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Shadcn/ui setup
npx shadcn-ui@latest init

# Charts for nutrition visualization
npm install recharts

# Date handling
npm install date-fns

# Icons
npm install lucide-react

# Forms
npm install react-hook-form @hookform/resolvers zod
```

#### 3.3 Configure TailwindCSS

**File: `frontend/tailwind.config.js`**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom brand colors
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        // Macro colors
        protein: '#ef4444',  // Red
        carbs: '#3b82f6',    // Blue
        fat: '#eab308',      // Yellow
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

#### 3.4 Setup API Client

**File: `frontend/src/services/api.ts`**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token (Phase 5)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

#### 3.5 Create Type Definitions

**File: `frontend/src/types/user.ts`**
```typescript
export interface User {
  id: number;
  name: string;
  age: number;
  sex: 'male' | 'female';
  height_inches: number;
  weight_lbs: number;
  body_fat_pct?: number;
  muscle_mass_lbs?: number;
  goal_type: 'bulk' | 'cut' | 'maintain' | 'recomp';
  activity_level: 'sedentary' | 'light' | 'moderate' | 'very_active' | 'athlete';
  training_days_per_week: number;
  cooking_skill: 'beginner' | 'intermediate' | 'advanced';
  cooking_frequency?: string;
  dietary_restrictions: string[];
  food_dislikes: string[];
  weekly_budget_usd: number;
  available_equipment: string[];
}

export interface BodyMetrics {
  id: number;
  user_id: number;
  date: string;
  weight_lbs: number;
  body_fat_pct?: number;
  muscle_mass_lbs?: number;
  waist_inches?: number;
  chest_inches?: number;
  arms_inches?: number;
  legs_inches?: number;
  notes?: string;
}

export interface ProgressSummary {
  status: string;
  period_days?: number;
  measurements_count?: number;
  starting_weight?: number;
  current_weight?: number;
  weight_change_lbs?: number;
  weight_change_pct?: number;
  starting_bodyfat?: number;
  current_bodyfat?: number;
  bodyfat_change_pct?: number;
  muscle_change_lbs?: number;
  message?: string;
}
```

**File: `frontend/src/types/meal.ts`**
```typescript
export type MealTime = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export interface MealLog {
  id: number;
  user_id: number;
  date: string;
  meal_time: MealTime;
  meal_name: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g?: number;
  sugar_g?: number;
  saturated_fat_g?: number;
  sodium_mg?: number;
  cholesterol_mg?: number;
  serving_size?: string;
  notes?: string;
  rating?: number;
  logged_at?: string;
}

export interface NutritionTotals {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
  saturated_fat_g: number;
  sodium_mg: number;
  cholesterol_mg: number;
}

export interface NutritionTargets {
  calories_target: number;
  protein_target_g: number;
  carbs_target_g: number;
  fat_target_g: number;
  fiber_target_g?: number;
  sugar_limit_g?: number;
  saturated_fat_limit_g?: number;
  sodium_limit_mg?: number;
  cholesterol_limit_mg?: number;
}

export interface DailyProgress {
  date: string;
  meals: MealLog[];
  meal_count: number;
  totals: NutritionTotals;
  targets: NutritionTargets;
  remaining: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    fiber_g: number;
  };
  percentages: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
  };
}

export interface MealRecommendation {
  id?: number;
  name: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  total_time_minutes?: number;
  difficulty?: string;
  cost_estimate_usd?: number;
  recommendation_score: number;
  match_reasons: string[];
  is_online_recipe: boolean;
  api_recipe_id?: string;
  nutrition_validated?: boolean;
}
```

#### 3.6 Create Layout Components

**File: `frontend/src/components/layout/Layout.tsx`**
```tsx
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export function Layout() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

**File: `frontend/src/components/layout/Sidebar.tsx`**
```tsx
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UtensilsCrossed,
  Apple,
  Package,
  Calendar,
  DollarSign,
  Settings,
} from 'lucide-react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/meals', icon: UtensilsCrossed, label: 'Meal Tracker' },
  { path: '/nutrition', icon: Apple, label: 'Nutrition' },
  { path: '/inventory', icon: Package, label: 'Inventory' },
  { path: '/planner', icon: Calendar, label: 'Weekly Planner' },
  { path: '/budget', icon: DollarSign, label: 'Budget' },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-white shadow-md">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-primary-600">🍳 Macro Chef</h1>
      </div>
      <nav className="mt-6">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center px-6 py-3 text-gray-700 hover:bg-primary-50 hover:text-primary-600 transition-colors ${
                isActive ? 'bg-primary-50 text-primary-600 border-r-4 border-primary-600' : ''
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="absolute bottom-0 w-64 p-6">
        <NavLink
          to="/settings"
          className="flex items-center text-gray-500 hover:text-gray-700"
        >
          <Settings className="w-5 h-5 mr-3" />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}
```

#### 3.7 Setup Routing

**File: `frontend/src/App.tsx`**
```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { MealTracker } from './pages/MealTracker';
import { Nutrition } from './pages/Nutrition';
import { Inventory } from './pages/Inventory';
import { WeeklyPlanner } from './pages/WeeklyPlanner';
import { Budget } from './pages/Budget';
import { Settings } from './pages/Settings';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="meals" element={<MealTracker />} />
            <Route path="nutrition" element={<Nutrition />} />
            <Route path="inventory" element={<Inventory />} />
            <Route path="planner" element={<WeeklyPlanner />} />
            <Route path="budget" element={<Budget />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

---

## Phase 4: Frontend Feature Implementation (Week 3-4)

### Goals
- Implement all pages matching current Tkinter functionality
- Create reusable components for nutrition display
- Add interactive charts and visualizations

### 4.1 Dashboard Page

**File: `frontend/src/pages/Dashboard.tsx`**
```tsx
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { MacroProgressCard } from '../components/dashboard/MacroProgressCard';
import { TodaysMeals } from '../components/dashboard/TodaysMeals';
import { QuickActions } from '../components/dashboard/QuickActions';
import { WeightChart } from '../components/dashboard/WeightChart';

export function Dashboard() {
  const userId = 1; // TODO: Get from auth context
  
  const { data: progress, isLoading: progressLoading } = useQuery({
    queryKey: ['dailyProgress', userId],
    queryFn: () => api.get(`/meals/progress?user_id=${userId}`).then(r => r.data),
  });

  const { data: user } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => api.get(`/users/${userId}`).then(r => r.data),
  });

  if (progressLoading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name || 'Chef'}! 👋
        </h1>
        <p className="text-gray-500 mt-1">
          Here's your nutrition summary for today
        </p>
      </div>

      {/* Macro Progress Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MacroProgressCard
          label="Calories"
          current={progress?.totals.calories || 0}
          target={progress?.targets.calories_target || 2000}
          unit="kcal"
          color="bg-green-500"
        />
        <MacroProgressCard
          label="Protein"
          current={progress?.totals.protein_g || 0}
          target={progress?.targets.protein_target_g || 150}
          unit="g"
          color="bg-red-500"
        />
        <MacroProgressCard
          label="Carbs"
          current={progress?.totals.carbs_g || 0}
          target={progress?.targets.carbs_target_g || 200}
          unit="g"
          color="bg-blue-500"
        />
        <MacroProgressCard
          label="Fat"
          current={progress?.totals.fat_g || 0}
          target={progress?.targets.fat_target_g || 70}
          unit="g"
          color="bg-yellow-500"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Meals */}
        <div className="lg:col-span-2">
          <TodaysMeals meals={progress?.meals || []} />
        </div>

        {/* Quick Actions */}
        <div>
          <QuickActions />
        </div>
      </div>

      {/* Weight Progress Chart */}
      <WeightChart userId={userId} />
    </div>
  );
}
```

### 4.2 Macro Progress Component

**File: `frontend/src/components/dashboard/MacroProgressCard.tsx`**
```tsx
interface MacroProgressCardProps {
  label: string;
  current: number;
  target: number;
  unit: string;
  color: string;
}

export function MacroProgressCard({
  label,
  current,
  target,
  unit,
  color,
}: MacroProgressCardProps) {
  const percentage = Math.min((current / target) * 100, 100);
  const remaining = target - current;
  const isOver = current > target;

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold">
            {current.toFixed(0)}
            <span className="text-sm font-normal text-gray-400 ml-1">
              / {target} {unit}
            </span>
          </p>
        </div>
        <span
          className={`text-sm font-medium px-2 py-1 rounded-full ${
            isOver
              ? 'bg-red-100 text-red-600'
              : 'bg-green-100 text-green-600'
          }`}
        >
          {isOver ? `+${Math.abs(remaining).toFixed(0)}` : remaining.toFixed(0)} left
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`h-3 rounded-full transition-all duration-500 ${color} ${
            isOver ? 'bg-red-500' : ''
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <p className="text-xs text-gray-400 mt-2 text-right">
        {percentage.toFixed(0)}%
      </p>
    </div>
  );
}
```

### 4.3 Service Layer

**File: `frontend/src/services/mealService.ts`**
```typescript
import { api } from './api';
import type { MealLog, DailyProgress, MealRecommendation } from '../types/meal';

export const mealService = {
  async logMeal(userId: number, meal: Partial<MealLog>): Promise<MealLog> {
    const response = await api.post(`/meals/log?user_id=${userId}`, meal);
    return response.data;
  },

  async getDailyProgress(userId: number, date?: string): Promise<DailyProgress> {
    const params = new URLSearchParams({ user_id: String(userId) });
    if (date) params.append('target_date', date);
    const response = await api.get(`/meals/progress?${params}`);
    return response.data;
  },

  async getMealHistory(userId: number, days: number = 7): Promise<MealLog[]> {
    const response = await api.get(`/meals/history?user_id=${userId}&days=${days}`);
    return response.data;
  },

  async deleteMeal(mealId: number): Promise<void> {
    await api.delete(`/meals/${mealId}`);
  },

  async getRecommendations(
    userId: number,
    mealTime: string,
    options?: { maxTime?: number; budgetLimit?: number }
  ): Promise<MealRecommendation[]> {
    const params = new URLSearchParams({
      user_id: String(userId),
      meal_time: mealTime,
    });
    if (options?.maxTime) params.append('max_time', String(options.maxTime));
    if (options?.budgetLimit) params.append('budget_limit', String(options.budgetLimit));
    
    const response = await api.get(`/meals/recommendations?${params}`);
    return response.data;
  },
};
```

### 4.4 Custom Hooks

**File: `frontend/src/hooks/useDailyProgress.ts`**
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mealService } from '../services/mealService';
import type { MealLog } from '../types/meal';

export function useDailyProgress(userId: number, date?: string) {
  return useQuery({
    queryKey: ['dailyProgress', userId, date],
    queryFn: () => mealService.getDailyProgress(userId, date),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

export function useLogMeal(userId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (meal: Partial<MealLog>) => mealService.logMeal(userId, meal),
    onSuccess: () => {
      // Invalidate and refetch daily progress
      queryClient.invalidateQueries({ queryKey: ['dailyProgress', userId] });
    },
  });
}

export function useDeleteMeal(userId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (mealId: number) => mealService.deleteMeal(mealId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dailyProgress', userId] });
    },
  });
}

export function useMealRecommendations(
  userId: number,
  mealTime: string,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ['recommendations', userId, mealTime],
    queryFn: () => mealService.getRecommendations(userId, mealTime),
    enabled,
  });
}
```

---

## Phase 5: Authentication & Multi-User (Week 4)

### Goals
- Implement JWT authentication
- Add user registration and login
- Secure all API endpoints

### 5.1 Backend Auth Implementation

**File: `backend/app/auth/jwt.py`**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return TokenData(user_id=user_id)
    except JWTError:
        return None
```

**File: `backend/app/auth/dependencies.py`**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt import decode_token
from app.services import UserProfileManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    user_manager = UserProfileManager()
    user = user_manager.get_user(token_data.user_id)
    
    if user is None:
        raise credentials_exception
    
    return user
```

### 5.2 Frontend Auth Context

**File: `frontend/src/contexts/AuthContext.tsx`**
```tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '../services/api';
import type { User } from '../types/user';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
  // ... other fields
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored token on mount
    const token = localStorage.getItem('token');
    if (token) {
      api.get('/users/me')
        .then(res => setUser(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user } = response.data;
    localStorage.setItem('token', access_token);
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const register = async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    const { access_token, user } = response.data;
    localStorage.setItem('token', access_token);
    setUser(user);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

---

## Phase 6: Testing & Deployment (Week 5)

### 6.1 Backend Testing

**File: `backend/tests/test_meals.py`**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_log_meal():
    response = client.post(
        "/api/meals/log?user_id=1",
        json={
            "meal_name": "Test Meal",
            "calories": 500,
            "protein_g": 30,
            "carbs_g": 50,
            "fat_g": 20,
            "meal_time": "lunch"
        }
    )
    assert response.status_code == 201
    assert response.json()["meal_name"] == "Test Meal"

def test_get_daily_progress():
    response = client.get("/api/meals/progress?user_id=1")
    assert response.status_code == 200
    assert "totals" in response.json()
    assert "targets" in response.json()
```

### 6.2 Docker Configuration

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/macrochef
      - SPOONACULAR_API_KEY=${SPOONACULAR_API_KEY}
    depends_on:
      - db
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=macrochef
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

**File: `backend/Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**File: `frontend/Dockerfile`**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
```

### 6.3 Deployment Options

#### Option A: Railway (Recommended for simplicity)
1. Connect GitHub repo to Railway
2. Configure environment variables
3. Deploy backend and frontend as separate services
4. Add PostgreSQL addon

#### Option B: Render
1. Create Web Service for backend
2. Create Static Site for frontend
3. Add PostgreSQL database

#### Option C: Self-hosted (VPS)
1. Use docker-compose on a VPS (DigitalOcean, Linode, etc.)
2. Add nginx as reverse proxy
3. Configure SSL with Let's Encrypt

---

## Database Migration Strategy

### SQLite → PostgreSQL Migration

1. **Export existing data:**
```bash
sqlite3 database/meal_planner.db .dump > backup.sql
```

2. **Create PostgreSQL database:**
```bash
createdb macrochef
```

3. **Use Alembic for schema management:**
```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

4. **Import data using pgloader:**
```bash
pgloader sqlite:///path/to/meal_planner.db postgresql://user:pass@localhost/macrochef
```

---

## API Specification

### Complete Endpoint List

| Method | Endpoint | Description |
|--------|----------|-------------|
| **Users** |||
| POST | `/api/users` | Create user |
| GET | `/api/users/{id}` | Get user |
| PATCH | `/api/users/{id}` | Update user |
| POST | `/api/users/{id}/metrics` | Log body metrics |
| GET | `/api/users/{id}/metrics` | Get metrics history |
| GET | `/api/users/{id}/progress` | Get progress summary |
| **Meals** |||
| POST | `/api/meals/log` | Log meal |
| GET | `/api/meals/progress` | Get daily progress |
| GET | `/api/meals/history` | Get meal history |
| GET | `/api/meals/weekly-summary` | Get weekly summary |
| DELETE | `/api/meals/{id}` | Delete meal |
| PATCH | `/api/meals/{id}/rating` | Update rating |
| GET | `/api/meals/recommendations` | Get recommendations |
| **Nutrition** |||
| POST | `/api/nutrition/targets` | Generate targets |
| GET | `/api/nutrition/targets` | Get today's targets |
| GET | `/api/nutrition/targets/{date}` | Get targets for date |
| **Inventory** |||
| GET | `/api/inventory` | List items |
| POST | `/api/inventory` | Add item |
| GET | `/api/inventory/{id}` | Get item |
| PATCH | `/api/inventory/{id}` | Update item |
| DELETE | `/api/inventory/{id}` | Delete item |
| POST | `/api/inventory/{id}/use` | Use item |
| GET | `/api/inventory/expiring` | Get expiring items |
| GET | `/api/inventory/summary` | Get summary |
| **Plans** |||
| POST | `/api/plans/generate` | Generate plan |
| POST | `/api/plans` | Save plan |
| GET | `/api/plans` | List plans |
| GET | `/api/plans/{id}` | Get plan |
| GET | `/api/plans/{id}/shopping-list` | Get shopping list |
| **Budget** |||
| GET | `/api/budget/weekly` | Weekly summary |
| GET | `/api/budget/monthly` | Monthly summary |
| GET | `/api/budget/trends` | Spending trends |
| GET | `/api/budget/categories` | Category breakdown |
| **Recipes** |||
| GET | `/api/recipes/search` | Search online recipes |
| GET | `/api/recipes/{id}` | Get recipe details |

---

## Component Mapping

| Tkinter Tab | React Page | Key Components |
|-------------|------------|----------------|
| Dashboard | `/` | MacroProgressCard, TodaysMeals, WeightChart |
| Meal Tracker | `/meals` | MealLogForm, MealList, QuickLog |
| Nutrition | `/nutrition` | MacroChart, MicronutrientTable, TargetsForm |
| Inventory | `/inventory` | InventoryTable, AddItemModal, ExpiringAlert |
| Weekly Planner | `/planner` | WeekCalendar, MealSlot, ShoppingList |
| Budget | `/budget` | SpendingChart, CategoryBreakdown, BudgetProgress |

---

## Tech Stack Details

### Backend
- **FastAPI** - Modern async Python web framework
- **Pydantic** - Data validation using Python type hints
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS
- **Shadcn/ui** - Pre-built accessible components
- **React Query** - Server state management
- **React Router** - Client-side routing
- **Zustand** - Client state management
- **Recharts** - Data visualization
- **React Hook Form + Zod** - Form handling and validation

### Infrastructure
- **Docker** - Containerization
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **nginx** - Reverse proxy (production)

---

## Next Steps Checklist

### Week 1: Backend Foundation
- [ ] Create backend directory structure
- [ ] Set up FastAPI with CORS
- [ ] Link existing scripts as services
- [ ] Create health check endpoint
- [ ] Test with Swagger UI

### Week 2: API Implementation
- [ ] Create all Pydantic schemas
- [ ] Implement user endpoints
- [ ] Implement meal endpoints
- [ ] Implement remaining endpoints
- [ ] Write API tests

### Week 3: Frontend Setup
- [ ] Initialize Vite + React + TypeScript
- [ ] Configure TailwindCSS + Shadcn/ui
- [ ] Create layout components
- [ ] Set up routing
- [ ] Create API client

### Week 4: Frontend Features
- [ ] Build Dashboard page
- [ ] Build Meal Tracker page
- [ ] Build remaining pages
- [ ] Add charts and visualizations
- [ ] Polish UI/UX

### Week 5: Auth & Deployment
- [ ] Implement JWT authentication
- [ ] Add login/register pages
- [ ] Configure Docker
- [ ] Set up CI/CD
- [ ] Deploy to production

---

## Questions?

If you need clarification on any section or want me to implement specific parts of this plan, let me know! I can:

1. Generate complete code for any specific router or component
2. Create the full Pydantic schema files
3. Build out specific React pages in detail
4. Help with Docker configuration
5. Set up database migrations with Alembic

Good luck with your migration!
