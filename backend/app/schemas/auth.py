"""
Authentication-related Pydantic schemas.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=13, le=120)
    sex: Optional[str] = Field(None, pattern="^(male|female)$")
    height_inches: Optional[float] = Field(None, gt=0, le=120)
    weight_lbs: Optional[float] = Field(None, gt=0, le=1000)

class UserRegisterResponse(BaseModel):
    """User registration response."""
    id: int
    email: str
    name: str
    message: str = "User registered successfully"
