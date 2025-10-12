"""
Tortoise-ORM database initialization.
"""
from tortoise import Tortoise
from app.settings import get_logger, settings

logger = get_logger(__name__)

# Tortoise-ORM configuration
TORTOISE_ORM = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.daily_cache",
                "app.models.site_status",
                "app.models.user_preferences",
                "aerich.models" # This is required for migrations
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC"
}

async def init_db() -> None:
    """Initialize database connection."""
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        logger.info("Database connection established")

        # Generate schemas (only in development - use migrations in production)
        if settings.ENVIRONMENT == "development":
            await Tortoise.generate_schemas()
            logger.info("Database schemas generated")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise

async def close_db() -> None:
    """Close database connections."""
    try:
        await Tortoise.close_connections()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}", exc_info=True)
