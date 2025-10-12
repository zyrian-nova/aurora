"""
Settings configuration directory for Aurora.
"""
from app.settings.config import settings
from app.settings.logging import setup_logging, get_logger

# Initialize the global app logger when the module is imported
app_logger = setup_logging()

__all__ = ["settings", "app_logger", "get_logger", "setup_logging"]
