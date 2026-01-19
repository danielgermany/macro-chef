"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - use absolute path to existing database
    DATABASE_URL: str = "sqlite:///../database/meal_planner.db"
    
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
