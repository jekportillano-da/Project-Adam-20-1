from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from .auth_utils import auth_manager
from .database import db
from .models import User

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Dependency to get the current authenticated user.
    Checks both Authorization header and access_token cookie.
    Returns None if no valid token is provided (for optional auth).
    """
    token = None
    
    # First try to get token from Authorization header
    if credentials:
        token = credentials.credentials
    
    # If no header token, try to get from cookies
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        return None
    
    try:
        payload = auth_manager.verify_token(token)
        if payload is None:
            return None
        
        email = payload.get("sub")
        if email is None:
            return None
        
        user_data = db.get_user_by_email(email)
        if user_data is None:
            return None
        
        return User(**user_data)
    
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current authenticated user.
    Raises HTTPException if no valid user is authenticated.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    return current_user

async def optional_auth_with_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Dependency for optional authentication that directly uses request.
    Returns the user if authenticated, None otherwise.
    """
    return await get_current_user(request, credentials)

async def optional_auth(current_user: Optional[User] = Depends(get_current_user)) -> Optional[User]:
    """
    Dependency for optional authentication.
    Returns the user if authenticated, None otherwise.
    """
    return current_user
