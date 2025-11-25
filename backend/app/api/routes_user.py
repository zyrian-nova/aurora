"""
User management routes - Profile and preferences management.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.routes_auth import get_current_user
from app.settings import get_logger
from app.schemas import ErrorResponse, MessageResponse, PasswordChange, UserPrederencesSchema, UserPreferencesUpdate, UserResponse, UserUpdate
from app.services import change_user_password, delete_user, get_user_preferences, update_user_preferences, update_user_profile

logger = get_logger(__name__)

router = APIRouter(prefix="/user", tags=["User management"])

# Profile management
@router.put(
    "/profile",
    response_model=UserResponse,
    responses={
        200: {"description": "profile updated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid data"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    }
)
async def update_profile(update_data: UserUpdate, current_user: Annotated[UserUpdate, Depends(get_current_user)]) -> UserResponse:
    """Update current user's profile."""
    try:
        user = await update_user_profile(current_user.id,update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.info(f"Profile updated for user: {user.username}")

        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/change-password",
    response_model=MessageResponse,
    responses={
        200: {"description": "Password changed successfully"},
        400: {"model": ErrorResponse, "description": "Current password incorrect"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    }
)
async def change_password(password_data: PasswordChange, current_user: Annotated[UserUpdate, Depends(get_current_user)]) -> MessageResponse:
    """Change user's password."""
    success = await change_user_password(current_user.id, password_data.current_password, password_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    logger.info(f"Password changed for user: {current_user.username}")

    return MessageResponse(message="Password changed successfully")

@router.delete(
    "/account",
    response_model=MessageResponse,
    responses={
        200: {"description": "Account deleted successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    }
)
async def delete_account(current_user: Annotated[UserUpdate, Depends(get_current_user)]) -> MessageResponse:
    """Delete current user's account (soft delete - deactivates account)."""
    success = await delete_user(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info(f"Account deleted for user: {current_user.username}")

    return MessageResponse(message="Account successfully deleted")

# Preferences management
@router.get(
    "/preferences",
    response_model=UserPrederencesSchema,
    responses={
        200: {"description": "User preferences"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Preferences not found"},
    }
)
async def get_preferences(current_user: Annotated[UserPrederencesSchema, Depends(get_current_user)]) -> UserPrederencesSchema:
    """Get current user's preferences."""
    preferences = await get_user_preferences(current_user.id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )

    return UserPrederencesSchema.model_validate(preferences)

@router.put(
    "/preferences",
    response_model=UserPrederencesSchema,
    responses={
        200: {"description": "Preferences updated successfully"},
        401: {"model": ErrorResponse, "description": "Not suthenticated"},
    }
)
async def update_preferences(preferences_data: UserPreferencesUpdate, current_user: Annotated[UserPrederencesSchema, Depends(get_current_user)]) -> UserPrederencesSchema:
    """Update user preferences."""
    preferences = await update_user_preferences(current_user.id, preferences_data)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info(f"Preferences updated for user: {current_user.username}")

    return UserPrederencesSchema.model_validate(preferences)
