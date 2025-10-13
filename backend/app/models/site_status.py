"""
Site status check history.
"""
import uuid
from datetime import datetime
from tortoise import fields
from tortoise.models import Model

class SiteStatus(Model):
    """Historical status checks for monitored websites."""
    # Type of ID is UUID
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    site = fields.ForeignKeyField(
        "models.MonitoredSite",
        related_name="status_checks",
        on_delete=fields.CASCADE
    )
    user = fields.ForeignKeyField(
        "models.User",
        related_name="site_checks",
        on_delete=fields.CASCADE
    )

    # Status check results
    is_up = fields.BooleanField(default=True)
    status_code = fields.IntField(null=True)
    response_time_ms = fields.IntField(
        null=True,
        description="Response time in miliseconds"
    )

    # Timestamps
    checked_at = fields.DatetimeField(
        default=datetime.now(datetime.UTC),
        index=True
    )

    class Meta: # type: ignore
        table = "site_status"
        ordering = ["-checked_at"]
        indexes = [
            ("site_id", "checked_at"),
            ("user_id", "checked_at"),
        ]

    def __str__(self) -> str:
        status = "UP" if self.is_up else "DOWN"
        return f"SiteStatus({self.site_id} - {status})"
