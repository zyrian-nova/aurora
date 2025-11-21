"""
Settings configuration directory for Aurora.
"""
from app.settings.config import settings
from app.settings.logging import setup_logging, get_logger
from app.settings.security import (
    hash_password,
    verify_password,
    needs_rehash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_id_from_token,
    verify_token_type,
    is_token_expired,
    validate_password_strength,
)

# Initialize the global app logger when the module is imported
app_logger = setup_logging()

__all__ = [
    "settings",
    "app_logger",
    "get_logger",
    "setup_logging",
    "hash_password",
    "verify_password",
    "needs_rehash",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_user_id_from_token",
    "verify_token_type",
    "is_token_expired",
    "validate_password_strength",
]
