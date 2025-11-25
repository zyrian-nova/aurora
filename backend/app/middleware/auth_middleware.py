"""
Authentication middleware and dependencies.
Reusable FastAPI dependencies for JWT authentication.
"""
from uuid import UUID
from typing import Annotated
from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.models import User
from app.settings import get_logger, verify_token_type, get_user_id_from_token
from app.services import get_user_by_id

logger = get_logger(__name__)

# Security scheme for bearer tokens
security = HTTPBearer()

# Token extraction & validation
async def get_token_from_header(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> str:
    """Extract JWT token from Authorization header."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials

async def verify_access_token(token: Annotated[str, Depends(get_token_from_header)]) -> UUID:
    """Verify that token is a valid access token and extract user ID."""
    # Verify it's an access token (not refresh)
    if not verify_token_type(token, "access"):
        logger.warning("Invalid token type used for authentication")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token
    user_id = get_user_id_from_token(token)
    if not user_id:
        logger.warning("Invalid or expired access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id

# User dependencies
async def get_current_user(user_id: Annotated[UUID, Depends(verify_access_token)]) -> User:
    """Get current authenticated user from database."""
    user = await get_user_by_id(user_id)

    if not user:
        logger.error(f"User not found for valid token: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    logger.debug(f"Authenticated user: {user.username}")
    return user

async def get_current_active_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get current active user (same as get_current_user but more explicit)."""
    # Already checked in get_current_user, but keeping for explicitness
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user

async def get_current_superuser(user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get current user and verify they are a superuser (admin)."""
    if not user.is_superuser:
        logger.warning(f"Non-superuser attempted admin access: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user

# Optional authentication if needed

# Refresh token validation
async def verify_refresh_token(token: Annotated[str, Depends(get_token_from_header)]) -> UUID:
    """Verify that token is a valid refresh token and extract user ID."""
    # Verify it's a refresh token and not an access token
    if not verify_token_type(token, "refresh"):
        logger.warning("Invalid token type for refresh")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract ID
    user_id = get_user_id_from_token(token)
    if not user_id:
        logger.warning("Invalid or expired refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id

# Covenience functions
async def get_current_user_id(user: Annotated[User, Depends(get_current_user)]) -> UUID:
    """Get just the current user's ID (convenience wrapper)."""
    return user.id

async def get_current_username(user: Annotated[User, Depends(get_current_user)]) -> str:
    """Get just the user's username (convenience wrapper)."""
    return user.username
