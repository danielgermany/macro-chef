"""
Authentication API endpoints (login, register).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt import create_access_token, verify_password, get_password_hash
from app.auth.dependencies import get_current_user
from app.schemas.auth import Token, UserLogin, UserRegister, UserRegisterResponse, PasswordChange, EmailChange
from app.services import UserProfileManager
from app.schemas.user import UserResponse

router = APIRouter()

def get_user_manager() -> UserProfileManager:
    """Dependency to get UserProfileManager instance."""
    return UserProfileManager()

@router.post("/register", response_model=UserRegisterResponse, status_code=201)
async def register(
    user_data: UserRegister,
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Register a new user."""
    import json
    import os
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"auth.py:20","message":"Register endpoint called","data":{"email":user_data.email,"hasName":bool(user_data.name)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"}) + '\n')
    # #endregion
    # Check if email already exists
    existing_user = manager.get_user_by_email(user_data.email)
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"auth.py:27","message":"Email check result","data":{"emailExists":bool(existing_user)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"}) + '\n')
    # #endregion
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = get_password_hash(user_data.password)
    
    # Create user with email and password
    try:
        # #region agent log
        with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"auth.py:47","message":"Creating user with auth","data":{"email":user_data.email,"hasAge":user_data.age is not None,"hasSex":user_data.sex is not None,"hasHeight":user_data.height_inches is not None,"hasWeight":user_data.weight_lbs is not None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"post-fix","hypothesisId":"A"}) + '\n')
        # #endregion
        # Only pass optional fields if they are provided (not None)
        # This allows create_user_with_auth to use its default values
        create_kwargs = {
            "email": user_data.email,
            "password_hash": password_hash,
            "name": user_data.name,
        }
        if user_data.age is not None:
            create_kwargs["age"] = user_data.age
        if user_data.sex is not None:
            create_kwargs["sex"] = user_data.sex
        if user_data.height_inches is not None:
            create_kwargs["height_inches"] = user_data.height_inches
        if user_data.weight_lbs is not None:
            create_kwargs["weight_lbs"] = user_data.weight_lbs
        
        user_id = manager.create_user_with_auth(**create_kwargs)
        # #region agent log
        with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"auth.py:58","message":"User created successfully","data":{"userId":user_id},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"post-fix","hypothesisId":"A"}) + '\n')
        # #endregion
        return UserRegisterResponse(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            message="User registered successfully"
        )
    except Exception as e:
        # #region agent log
        with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"auth.py:71","message":"Registration error","data":{"error":str(e),"errorType":type(e).__name__},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"post-fix","hypothesisId":"A"}) + '\n')
        # #endregion
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Login and get access token."""
    # OAuth2PasswordRequestForm uses 'username' field for email
    user = manager.get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-json", response_model=Token)
async def login_json(
    login_data: UserLogin,
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Login using JSON body (alternative to form data)."""
    import json
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"auth.py:82","message":"Login endpoint called","data":{"email":login_data.email},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + '\n')
    # #endregion
    user = manager.get_user_by_email(login_data.email)
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"auth.py:87","message":"User lookup result","data":{"userFound":bool(user),"userId":user.get("id") if user else None},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + '\n')
    # #endregion
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    password_valid = verify_password(login_data.password, user.get("password_hash", ""))
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"auth.py:96","message":"Password verification","data":{"passwordValid":password_valid,"hasPasswordHash":bool(user.get("password_hash"))},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + '\n')
    # #endregion
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    # #region agent log
    with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
        f.write(json.dumps({"location":"auth.py:104","message":"Token created","data":{"tokenLength":len(access_token),"userId":user["id"]},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"}) + '\n')
    # #endregion
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current authenticated user's information."""
    return current_user

@router.patch("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Change the current user's password."""
    import json
    import traceback
    # #region agent log
    try:
        with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"auth.py:151","message":"Change password endpoint called","data":{"userId":current_user.get("id")},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run2","hypothesisId":"H"}) + '\n')
    except: pass
    # #endregion
    user_id = current_user["id"]
    user = manager.get_user(user_id)
    # #region agent log
    try:
        with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"location":"auth.py:160","message":"User retrieved for password change","data":{"userFound":bool(user),"hasPasswordHash":bool(user.get("password_hash"))},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run2","hypothesisId":"H"}) + '\n')
    except: pass
    # #endregion

    if not user or not verify_password(password_data.current_password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid current password")

    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirmation do not match")

    try:
        new_password_hash = get_password_hash(password_data.new_password)
        # #region agent log
        try:
            with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"auth.py:170","message":"Password hash generated","data":{"hashLength":len(new_password_hash)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run2","hypothesisId":"H"}) + '\n')
        except: pass
        # #endregion
        manager.update_user_password(user_id, new_password_hash)
        # #region agent log
        try:
            with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"auth.py:172","message":"Password update called","data":{"userId":user_id},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run2","hypothesisId":"H"}) + '\n')
        except: pass
        # #endregion
        return {"message": "Password updated successfully"}
    except Exception as e:
        # #region agent log
        try:
            with open(r'd:\Projects\macro-chef\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"auth.py:175","message":"Password change error","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run2","hypothesisId":"H"}) + '\n')
        except: pass
        # #endregion
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Password update failed: {str(e)}")

@router.patch("/change-email")
async def change_email(
    email_data: EmailChange,
    current_user: dict = Depends(get_current_user),
    manager: UserProfileManager = Depends(get_user_manager)
):
    """Change the current user's email address."""
    user_id = current_user["id"]
    user = manager.get_user(user_id)

    if not user or not verify_password(email_data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    existing_user_with_new_email = manager.get_user_by_email(email_data.new_email)
    if existing_user_with_new_email and existing_user_with_new_email["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use by another account")

    manager.update_user_email(user_id, email_data.new_email)
    return {"message": "Email updated successfully"}
