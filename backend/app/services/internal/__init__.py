"""
Internal services - Business logic layer.
"""
from app.services.internal.user_service import (
    # User CRUD
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    get_user_with_preferences,
    update_user_profile,
    change_user_password,
    delete_user,
    # Authentication
    authenticate_user,
    validate_user_active,
    # Preferences
    get_user_preferences,
    update_user_preferences,
    # Statistics
    get_total_users,
    get_active_users,
    get_recent_users,
)

__all__ = [
    # User CRUD
    "create_user",
    "get_user_by_id",
    "get_user_by_email",
    "get_user_by_username",
    "get_user_with_preferences",
    "update_user_profile",
    "change_user_password",
    "delete_user",
    # Authentication
    "authenticate_user",
    "validate_user_active",
    # Preferences
    "get_user_preferences",
    "update_user_preferences",
    # Statistics
    "get_total_users",
    "get_active_users",
    "get_recent_users",
]
