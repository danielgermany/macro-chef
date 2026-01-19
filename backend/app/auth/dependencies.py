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
    import json
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"dependencies.py:12","message":"get_current_user called","data":{"hasToken":bool(token),"tokenLength":len(token) if token else 0},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"}) + '\n')
    # #endregion
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"dependencies.py:21","message":"Token decoded","data":{"tokenDataValid":bool(token_data),"userId":token_data.user_id if token_data else None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"}) + '\n')
    # #endregion
    if token_data is None:
        raise credentials_exception
    
    manager = UserProfileManager()
    user = manager.get_user(token_data.user_id)
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"dependencies.py:26","message":"User retrieved","data":{"userFound":bool(user),"userId":user.get("id") if user else None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"}) + '\n')
    # #endregion
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> int:
    """Get the current user's ID."""
    return current_user["id"]
