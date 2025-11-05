"""
Schemas for webdsite status monitoring.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl

# Monitored site schemas

class MonitoredSiteBase(BaseModel):
    """Base monitored site schema."""
    url: HttpUrl
    name: str = Field(min_length=1, max_length=255)

class MonitoredSiteCreate(MonitoredSiteBase):
    """Schema for creating monitored site."""
    check_interval_minutes: int = Field(default=5, ge=1, le=60)
    expected_status_code: int = Field(default=200)
    timeout_seconds: int = Field(default=10, ge=1, le=60)

class MonitoredSiteUpdate(BaseModel):
    """Schema for updating monitored site."""
    name: Optional[str] = Field(default=None, max_length=255)
    check_interval_minutes: Optional[int] = Field(defautl=None, ge=1, le=60)
    is_active: Optional[bool] = None

class MonitoredSiteResponse(MonitoredSiteBase):
    """Monitored site response."""
    id: UUID
    check_interval_minutes: int
    is_active: bool
    expected_status_code: int
    timeout_seconds: int
    created_at: datetime

    class Config:
        from_atttibiutes = True

# Status check schemas
class StatusCheckResponse(BaseModel):
    """Individual status check response."""
    id: UUID
    site_id: UUID
    is_up: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    checked_at: datetime

    class Config:
        from_attributes = True

class SiteStatusSummary(BaseModel):
    """Summary of site status."""
    site: MonitoredSiteResponse
    latest_check: Optional[StatusCheckResponse] = None
    uptime_percentage_7d: float = Field(ge=0, le=100)
    total_checks_7d: int = Field(ge=0)
    average_response_time_ms: Optional[float] = None

class AllSitesStatusResponse(BaseModel):
    """Status of all monitored sites."""
    sites: list[SiteStatusSummary]
    updated_at: datetime
