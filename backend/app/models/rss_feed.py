"""
RSS feed models
"""
import uuid
from tortoise import fields
from tortoise.models import Model

class RSSFeed(Model):
    """Catalog of RSS feeds available in the system."""
    # Type of ID is UUID
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    url = fields.CharField(
        max_length=500,
        unique=True,
        index=True
    )
    title = fields.CharField(
        max_length=255,
        null=True
    )
    description = fields.TextField(null=True)

    # Feed metadata
    site_url = fields.CharField(
        max_length=500,
        null=True
    )
    favicon_url = fields.CharField(
        max_length=500,
        null=True
    )
    language = fields.CharField(
        max_length=10,
        null=True
    )

    # Status
    is_active = fields.BooleanField(
        default=True,
        description="Whether this feed is still valid"
    )
    last_fetched_at = fields.DatetimeField(null=True)
    last_error = fields.TextField(null=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Relationships
    subscribers: fields.ReverseRelation["UserRSSFeed"]

    class Meta: # type: ignore
        table = "rss_feeds"
        ordering = ["title"]

    def __str__(self) -> str:
        return f"RSSFeed({self.title or self.url})"

class UserRSSFeed(Model):
    """Junction table: User subscriptions to RSS feeds"""
    # Type of ID is UUID
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    user = fields.ForeignKeyField(
        "models.User",
        related_name="rss_subscriptions",
        on_delete=fields.CASCADE
    )
    feed = fields.ForeignKeyField(
        "models.RSSFeed",
        related_name="subscribers",
        on_delete=fields.CASCADE
    )

    # User-specific settings for this feed
    custom_name = fields.CharField(
        max_length=255,
        null=True,
        description="User's custom name for this feed"
    )
    is_active = fields.BooleanField(
        default=True,
        description="User can pause individual feeds"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta: # type: ignore
        table = "user_rss_feeds"
        unique_together = (("user", "feed"),) # Prevent duplicate entries
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"UserRSSFeed(user={self.user_id}, feed={self.feed_id})"
