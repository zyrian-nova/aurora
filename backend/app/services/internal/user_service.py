"""
User service - Business logic for user operations.
Handles user creation, authentication, profile management and preferences.
"""
from uuid import UUID
from typing import Optional
from app.models import User, UserPreferences
from app.schemas import UserCreate, UserPreferencesUpdate, UserUpdate
from app.settings import get_logger, needs_rehash, verify_password
from app.settings import hash_password
from tortoise.exceptions import IntegrityError, DoesNotExist

logger = get_logger(__name__)

# User CRUD operations
async def create_user(user_data: UserCreate) -> User:
    """Create a new user with hashed password and default preferences."""
    # Check if email already exists
    existing_email = await User.filter(email=user_data.email).first()
    if existing_email:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise ValueError("Email already registered")

    # Check if username already exists
    existing_username = await User.filter(username=user_data.username).first()
    if existing_username:
        logger.warning(f"Registration attempt with existing username: {user_data.username}")
        raise ValueError("Username already taken")

    # Hash password
    hashed_password = hash_password(user_data.password)

    try:
        # Create user
        user = await User.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False
        )
        # Create default preferences
        await UserPreferences.create(user=user)

        logger.info(f"New user created: {user.username} ({user.email})")
        return user

    except IntegrityError as e:
        logger.warning(f"Database integrity error creating user: {e}")
        raise ValueError("Unable to create user - data conflict")

async def get_user_by_id(user_id: UUID) -> Optional[User]:
    """Get user by UUID."""
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        return None

async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email address."""
    return await User.filter(email=email).first()

async def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    return await User.filter(username=username).first()

async def get_user_with_preferences(user_id: UUID) -> Optional[User]:
    """Get user with their preferences prefetched."""
    try:
        return await User.get(id=user_id).prefetch_related("preferences")
    except DoesNotExist:
        return None

async def update_user_profile(user_id: UUID, update_data: UserUpdate) -> Optional[User]:
    """Update user profile information."""
    user = await get_user_by_id(user_id)
    if not user:
        return None

    # Check email uniqueness if changing
    if update_data.email and update_data.email != user.email:
        existing = await User.filter(email=update_data.email).first()
        if existing:
            raise ValueError("Email already in use")
        user.email = update_data.email

    # Check username uniqueness if changing
    if update_data.username and update_data.username != user.username:
        existing = await User.filter(username=update_data.username).first()
        if existing:
            raise ValueError("Username already taken")
        user.username = update_data.username

    # Update full name if provided
    if update_data.full_name is not None:
        user.full_name = update_data.full_name

    await user.save()
    logger.info(f"Updated profile for user: {user.username}")
    return user

async def change_user_password(user_id: UUID, current_password: str, new_password: str) -> bool:
    """Change user's password after verifying current password."""
    user = await get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    # verify current password
    if not verify_password(current_password, user.hashed_password):
        logger.warning(f"Failed password change attempt for user: {user.username}")
        return False

    # Hash and set new password
    user.hashed_password = hash_password(new_password)
    await user.save(update_fields=["hashed_password", "updated_at"])

    logger.info(f"Password changed for user: {user.username}")
    return True

async def delete_user(user_id: UUID) -> bool:
    """Delete user account (soft delete - set inactive)."""
    user = await get_user_by_id(user_id)
    if not user:
        return False

    # Soft delete - just deactivate
    user.is_active = False
    await user.save(update_fields=["is_active", "updated_at"])

    logger.info(f"User deactivated: {user.username}")
    return True

# Authentication logic
async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Aunthentocate user with email and password."""
    user = await get_user_by_email(email)
    if not user:
        logger.debug(f"Authentication failed: user not found ({email})")
        return None

    if not user.is_active:
        logger.warning(f"Authentication attempt for inactive user: ({email})")
        return None

    # Verify password
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: wrong password ({email})")
        return None

    # Check if password hash needs upgrade (Argon2 parameters changed)
    if needs_rehash(user.hashed_password):
        logger.info(f"Upgrading password hash for user: {user.username}")
        user.hashed_password = hash_password(password)
        await user.save(update_fields=["hashed_password", "updated_at"])

    # Update last login
    await user.update_last_login()
    logger.info(f"User authenticated: {user.username}")
    return user

async def validate_user_active(user_id: UUID) -> bool:
    """Check if the user exists and is active."""
    user = await get_user_by_id(user_id)
    return user is not None and user.is_active

# User preferences
async def get_user_preferences(user_id: UUID) -> Optional[UserPreferences]:
    """Get user's preferences."""
    return await UserPreferences.filter(user_id=user_id).first()

async def update_user_preferences(user_id: UUID, preferences_data: UserPreferencesUpdate) -> Optional[UserPreferences]:
    """Update user preferences."""
    preferences = await get_user_preferences(user_id)
    if not preferences:
        # Create preferences if they don't exist
        user = await get_user_by_id(user_id)
        if not user:
            return None
        preferences = await UserPreferences.create(user=user)

    # Update fields that were provided
    if preferences_data.word_languages is not None:
        preferences.word_languages = preferences_data.word_languages
    if preferences_data.prefered_language is not None:
        preferences.preferred_language = preferences_data.prefered_language
    if preferences_data.theme is not None:
        preferences.theme = preferences_data.theme
    if preferences_data.background_rotation is not None:
        preferences.background_rotation = preferences_data.background_rotation
    if preferences_data.location is not None:
        preferences.location = preferences_data.location

    await preferences.save()
    logger.info(f"Updated preferences for user_id: {user_id}")
    return preferences

# User statistics
async def get_total_users() -> int:
    """Get total number of registered users."""
    return await User.all().count()

async def get_active_users() -> int:
    """Get number of active users."""
    return await User.filter(is_active=True).count()

async def get_recent_users(limit: int = 10) -> list[User]:
    """Get most recentrly registered users."""
    return await User.filter(is_active=True).order_by("-created_at").limit(limit)
