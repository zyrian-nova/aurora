"""
Subreddit feed models
"""
import uuid
from tortoise import fields
from tortoise.models import Model

class Subreddit(Model):
    """Catalog of subreddits available in the system."""
    # Type of ID is UUID
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    name = fields.CharField(
        max_length=100,
        unique=True,
        index=True,
        description="Subreddit name (without r/ prefix)"
    )
    display_name = fields.CharField(
        max_length=100,
        null=True
    )
    description = fields.TextField(null=True)

    # Metadata
    subscriber_count = fields.IntField(
        null=True,
        description="Number of subscribers on Reddit"
    )
    icon_url = fields.CharField(
        max_length=500,
        null=True
    )

    # Status
    is_active = fields.BooleanField(
        default=True,
        description="Whether this subreddit still exists"
    )
    is_nsfw = fields.BooleanField(
        default=False,
        description="Whether this subreddit content is +18"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Relationships
    followers: fields.ReverseRelation["UserSubreddit"]

    class Meta: # type: ignore
        table = "subreddits"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"Subreddit(r/{self.name})"

class UserSubreddit(Model):
    """Junction table: User subscriptions to subreddits."""
    # Type of ID is UUID
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    user = fields.ForeignKeyField(
        "models.User",
        related_name="subreddit_subscriptions",
        on_delete=fields.CASCADE
    )
    subreddit = fields.ForeignKeyField(
        "models.Subreddit",
        related_name="followers",
        on_delete=fields.CASCADE
    )

    # User-specific settings
    is_active = fields.BooleanField(
        default=True,
        description="Usee can pause individual subreddits"
    )
    sort_by = fields.CharField(
        max_length=20,
        default="hot",
        description="Sort preference: hot, new, top, rising"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta: # type: ignore
        table = "user_subreddits"
        unique_together = (("user", "subreddit"),) # Prevent duplicate entries
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"UserSubreddit(user={self.user_id}, subreddit={self.subreddit_id})"
