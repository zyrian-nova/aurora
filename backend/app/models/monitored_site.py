"""
Monitored website models.
"""
import uuid
from tortoise import fields
from typing import Optional
from models import SiteStatus
from tortoise.models import Model

class MonitoredSite(Model):
    """Websites that users want to monitor for uptime."""
    # Type of ID is UUID
    id = fields.UUIDField(
        pk=True,
        default=uuid.uuid4
    )
    user = fields.ForeignKeyField(
        "models.User",
        related_name="monitored_sites",
        on_delete=fields.CASCADE
    )

    # Site information
    url = fields.CharField(
        max_length=500,
        description="Full URL to monitor (e.g., https://example.com)"
    )
    name = fields.CharField(
        max_length=255,
        description="Friendly name for display"
    )

    # Monitoring configuration
    check_interval_minutes = fields.IntField(
        default=30,
        description="How often to check (in minutes)"
    )
    is_active = fields.BooleanField(
        default=True,
        description="Whether monitoring is enabled"
    )

    # Expected response
    expected_status_code = fields.IntField(
        default=200,
        description="Expected HTTP status code"
    )
    timeout_in_seconds = fields.IntField(
        default=10,
        description="Request timeout in seconds"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Relationships
    status_checks: fields.ReverseRelation["SiteStatus"]

    class Meta: # type: ignore
        table = "monitored_sites"
        unique_together = (("user", "url"),) # Each user can only monitor one URL once
        ordering = ["name"]

    def __str__(self) -> str:
        return f"MonitoredSite({self.name} - {self.url})"

    async def get_latest_status(self) -> Optional["SiteStatus"]:
        """Get the most recent status check for this site."""
        from app.models import SiteStatus
        return await SiteStatus.filter(site=self).order_by("-checked_at").first()

    async def get_uptime_percentage(self, days: int = 7) -> float:
        """Calculate uptime percentage for the last N days."""
        from datetime import datetime, timedelta
        from app.models.site_status import SiteStatus

        since = datetime.now(datetime.UTC) - timedelta(days=days)

        total = await SiteStatus.filter(
            site=self,
            checked_at__gte=since
        ).count()

        if total == 0:
            return 100.0

        up_count = await SiteStatus.filter(
            site=self,
            checked_at__gte=since,
            is_up=True
        ).count()

        return (up_count / total) * 100
