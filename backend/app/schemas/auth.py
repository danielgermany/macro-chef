"""
Authentication-related Pydantic schemas.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    height_inches: Optional[float] = None
    weight_lbs: Optional[float] = None

class UserRegisterResponse(BaseModel):
    id: int
    email: str
    name: str
    message: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters")
    confirm_password: str = Field(..., min_length=8, description="Password confirmation must match new password")

class EmailChange(BaseModel):
    new_email: EmailStr
    password: str  # Require password confirmation for security
