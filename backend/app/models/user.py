"""
User model for authentication.
"""
import uuid
from tortoise import fields
from datetime import datetime, timezone
from tortoise.models import Model
from app.models.rss_feed import UserRSSFeed
from app.models.site_status import SiteStatus
from app.models.subreddit import UserSubreddit
from app.models.monitored_site import MonitoredSite
from app.models.user_preferences import UserPreferences


class User(Model):
    """User account model."""
    # Type of ID is UUID
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    email = fields.CharField(
        max_length=100,
        unique=True,
        index=True
    )
    username = fields.CharField(
        max_length=100,
        unique=True,
        index=True
    )
    hashed_password = fields.CharField(max_length=255)

    # Profile
    full_name = fields.CharField(
        max_length=255,
        null=True
    )
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_login = fields.DatetimeField(null=True)

    # Relationships
    preferences: fields.ReverseRelation["UserPreferences"]
    rss_subscriptions: fields.ReverseRelation["UserRSSFeed"]
    subreddit_subscriptions: fields.ReverseRelation["UserSubreddit"]
    monitored_sites: fields.ReverseRelation["MonitoredSite"]
    site_checks: fields.ReverseRelation["SiteStatus"]

    class Meta: # type: ignore
        table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"User({self.username}, {self.email})"

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"

    async def update_last_login(self) -> None:
        """Update the last_login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        await self.save(update_fields=["last_login"])
