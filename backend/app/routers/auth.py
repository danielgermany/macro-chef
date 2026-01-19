"""
Authentication API endpoints (login, register).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt import create_access_token, verify_password, get_password_hash
from app.auth.dependencies import get_current_user
from app.schemas.auth import Token, UserLogin, UserRegister, UserRegisterResponse
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
    # Check if email already exists
    existing_user = manager.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = get_password_hash(user_data.password)
    
    # Create user with email and password
    try:
        user_id = manager.create_user_with_auth(
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name
        )
        return UserRegisterResponse(
            id=user_id,
            email=user_data.email,
            name=user_data.name
        )
    except Exception as e:
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
    user = manager.get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current authenticated user's information."""
    return current_user
