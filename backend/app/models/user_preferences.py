"""
User preferences model.
"""
import uuid
from tortoise import fields
from tortoise.models import Model

class UserPreferences(Model):
    """User-specific preferences and settings."""
    # Type of ID is UUID
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.OneToOneField(
        "models.User",
        related_name="preferences",
        on_delete=fields.CASCADE
    )

    # Language preferences (as JSON)
    word_languages = fields.JSONField(
        default=["en", "es", "fi"],
        description="Languages for word of the day (ISO 639-1 codes)"
    )
    preferred_language = fields.CharField(
        max_length=10,
        default="en",
        description="Primary UI language"
    )

    # Display preferences
    theme = fields.CharField(
        max_length=20,
        default="auto",
        description="Theme: light, dark, auto"
    )
    background_rotation = fields.BooleanField(
        default=True,
        description="Enable daily background image rotation"
    )

    # Location for weather
    location = fields.CharField(
        max_length=255,
        null=True,
        description="City name or coordinates for weather (e.g., 'Helsinki' or '60.1699,24.9384')"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta: # type: ignore
        table = "user_preferences"

    def __str__(self) -> str:
        return f"Preferences(user={self.user_id})"
