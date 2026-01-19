"""
Online recipe search Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class RecipeSearchParams(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    max_results: int = Field(5, ge=1, le=20)
    max_calories: Optional[int] = Field(None, ge=100)
    min_protein: Optional[int] = Field(None, ge=0)
    max_ready_time: Optional[int] = Field(None, ge=1)

class RecipeSearchResponse(BaseModel):
    id: int
    title: str
    readyInMinutes: int
    nutrition: dict
    is_validated: bool = False
