"""
Authentication dependencies for FastAPI routes.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt import decode_token
from app.services import UserProfileManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    manager = UserProfileManager()
    user = manager.get_user(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> int:
    """Get the current user's ID."""
    return current_user["id"]
