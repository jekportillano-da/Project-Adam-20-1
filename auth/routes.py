from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from datetime import timedelta
import logging
from .models import UserCreate, UserLogin, Token, UserResponse
from .auth_utils import auth_manager
from .database import db
from .dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        hashed_password = auth_manager.get_password_hash(user_data.password)
        
        # Create the user
        user_id = db.create_user(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Get the created user
        new_user = db.get_user_by_id(user_id)
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created user"
            )
        
        return UserResponse(**new_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login")
async def login_user(user_credentials: UserLogin):
    """Login user and return access token with cookie"""
    try:
        # Authenticate the user
        user = auth_manager.authenticate_user(
            email=user_credentials.email,
            password=user_credentials.password,
            db_instance=db
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=auth_manager.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": user["email"]}, 
            expires_delta=access_token_expires
        )
        
        # Create response with token
        response = JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer"
            }
        )
        
        # Set the token as an httpOnly cookie for security
        # Import config for cookie settings
        try:
            from config import Settings
            settings = Settings()
        except ImportError:
            # Fallback settings for development
            class FallbackSettings:
                cookie_secure = False
                cookie_samesite = "lax"
                cookie_domain = None
                cookie_path = "/"
            settings = FallbackSettings()
        
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=int(access_token_expires.total_seconds()),
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",  # Use literal for type safety
            path=settings.cookie_path,
            domain=settings.cookie_domain
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout_user():
    """Logout user by clearing the access token cookie"""
    response = JSONResponse(content={"message": "Successfully logged out"})
    response.delete_cookie(key="access_token", path="/", domain=None)
    return response

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user
