"""
Authentication routes - Register, login, refresh, and user info endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.settings import create_access_token, create_refresh_token, get_logger, get_user_id_from_token, verify_token_type
from app.schemas import ErrorResponse, LoginRequest, MessageResponse, RefreshTokenRequest, TokenResponse, UserCreate, UserResponse, UserWithPreferences
from app.services import authenticate_user, create_user, get_user_by_id, get_user_with_preferences

logger = get_logger(__name__)

# Router instance
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()

# Helper functions
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract and validate user ID from JWT token."""
    token = credentials.credentials

    # Verify it's an access token (not refresh token)
    if not verify_token_type(token, "access"):
        logger.warning("Invalid token type user for authentication")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID
    user_id = get_user_id_from_token(token)
    if not user_id:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return str(user_id)

# Public endpoints
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User successfully registered"},
        400: {"model": ErrorResponse, "description": "Validation error or duplicate user"},
    }
)
async def register(user_data: UserCreate) -> UserResponse:
    """Register a new user account."""
    try:
        user = await create_user(user_data)
        logger.info(f"New user registered: {user.username}")
        return UserResponse.model_validate(user)
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        200: {"description": "Successfully authenticated"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    }
)
async def login(credentials: LoginRequest) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id)
    logger.info(f"User logged in: {user.username}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        200: {"description": "Tokens refreshed successfully"},
        402: {"model": ErrorResponse, "description": "Invalid refresh token"},
    }
)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """Get new access token using refresh token."""
    # Verify if it's a refresh token
    if not verify_token_type(request.refres_token, "refresh"):
        logger.warning("Invalid token type for refresh")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID
    user_id = get_user_id_from_token(request.refres_token)
    if not user_id:
        logger.warning("Invalid or expired refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user to verify they still exist and are active
    user = await get_user_by_id(user_id)
    if not user or not user.is_active:
        logger.warning(f"Refresh attempt for inactive/deleted user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate new tokens
    new_access_token = create_access_token(user.id, user.username)
    new_refresh_token = create_refresh_token(user.id)
    logger.info(f"Tokens refreshed for user: {user.username}")

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )

# Protected endpoints
@router.get(
    "/me",
    response_model=UserWithPreferences,
    responses={
        200: {"description": "Current user information"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    }
)
async def get_current_user(user_id: str = Depends(get_current_user_id)) -> UserWithPreferences:
    """Get current authenticade user's information."""
    from uuid import UUID

    # Extract the user ID
    user = await get_user_with_preferences(UUID(user_id))
    if not user:
        logger.error(f"User not found for valid token: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify if the user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    logger.debug(f"User info requested: {user.username}")

    return UserWithPreferences.model_validate(user)

@router.post(
    "/logout",
    response_model=MessageResponse,
    responses={
        200: {"description": "Successfully logged out"},
    }
)
async def logout(user_id: str = Depends(get_current_user_id)) -> MessageResponse:
    """
    Logout current user.

    Note: Since we use stateless JWT tokens, logout is handled client-side
    by deleting the stored tokens. This endpoint is mainly for logging purposes.

    In production, you might want to implement token blacklisting [TO DO LIST].
    """
    logger.info(f"User logged out: {user_id}")

    return MessageResponse(
        message="Successfully logged out. Please delete your tokens on the client side."
    )
