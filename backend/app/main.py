"""
Macro Chef API - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import users, meals, nutrition, inventory, plans, budget, recipes, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Create tables if they don't exist
    # Note: We're using existing SQLite database, so we don't create tables here
    # Base.metadata.create_all(bind=engine)
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
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
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
