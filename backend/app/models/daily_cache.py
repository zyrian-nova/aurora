"""
Daily cache model
"""
import uuid
from datetime import date
from tortoise import fields
from typing import Optional
from tortoise.models import Model

class DailyCache(Model):
    """Cache for daily generated content shared across all users."""
    # Type of ID is UUID
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    cache_date = fields.DateField(
        default=date.today,
        unique=True,
        index=True,
        description="Date this cache entry is valid for"
    )

    # Motivational content
    motivational_quote = fields.TextField(null=True)
    quote_author = fields.CharField(
        max_length=255,
        null=True
    )
    quote_source = fields.CharField(
        max_length=100,
        null=True,
        description="Source: ollama, api, static"
    )

    # Word of the day (multilingual)
    word_en = fields.JSONField(
        null=True,
        description="English: {word, definition, example, pronunciation}"
    )
    word_es = fields.JSONField(
        null=True,
        description="Spanish: {word, definition, example, pronunciation}"
    )
    word_fi = fields.JSONField(
        null=True,
        description="Finnish: {word, definition, example, pronunciation}"
    )

    # Weather cache (optional)
    weather_data = fields.JSONField(
        null=True,
        description="Last fetched global weather data (if applicable)"
    )

    # Generation metadata
    generated_by_ollama = fields.BooleanField(
        default=False,
        description="Whether content was AI-generated"
    )
    generation_model = fields.CharField(
        max_length=100,
        null=True,
        description="Ollama model used (e.g., llama3, mistral)"
    )
    generation_duration_ms = fields.IntField(
        null=True,
        description="Time taken to generate content (milliseconds)"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta: # type: ignore
        table = "daily_cache"
        ordering = ["-cache_date"]

    def __str__(self) -> str:
        return f"SailyCache({self.cache_date})"

    @classmethod
    async def get_today(cls) -> "DailyCache":
        """Get or create today's cache entry."""
        today = date.today()
        cache, _ = await cls.get_or_create(cache_date=today)
        return cache

    @classmethod
    async def get_latest(cls) -> Optional["DailyCache"]:
        """Get the most recent cache entry."""
        return await cls.all().order_by("-cache_date").first()
