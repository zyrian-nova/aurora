"""
Database models for Aurora.
"""
# import all models
from app.models.user import User
from app.models.user_preferences import UserPreferences

__all__ = [
    "User",
    "UserPreferences"
]
