"""
Pydantic schemas for API request/response validation.
"""
from app.schemas.user_schema import (
    UserBase,
    UserCreate,
    UserUpdate,
    PasswordChange,
    UserResponse,
    UserWithPreferences,
    UserPrederencesSchema,
    UserPreferencesUpdate,
)
from app.schemas.auth_schema import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    TokenPayloadResponse,
)
from app.schemas.response_schema import (
    SuccessResponse,
    MessageResponse,
    ErrorResponse,
    ValidationErrorResponse,
    PaginatedResponse,
)
from app.schemas.daily_schema import (
    WeatherData,
    QuoteData,
    WordData,
    MultilingualWord,
    DailyDataResponse,
)
from app.schemas.news_schema import (
    RSSFeedCreate,
    RSSFeedResponse,
    RSSItemResponse,
    SubredditCreate,
    SubredditResponse,
    RedditPostResponse,
    NewsResponse,
)
from app.schemas.status_schema import (
    MonitoredSiteCreate,
    MonitoredSiteUpdate,
    MonitoredSiteResponse,
    StatusCheckResponse,
    SiteStatusSummary,
    AllSitesStatusResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "PasswordChange",
    "UserResponse",
    "UserWithPreferences",
    "UserPrederencesSchema",
    "UserPreferencesUpdate",
    # Auth schemas
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "TokenPayloadResponse",
    # Response schemas
    "SuccessResponse",
    "MessageResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "PaginatedResponse",
    # Daily sata schema
    "WeatherData",
    "QuoteData",
    "WordData",
    "MultilingualWord",
    "DailyDataResponse",
    # News schemas
    "RSSFeedCreate",
    "RSSFeedResponse",
    "RSSItemResponse",
    "SubredditCreate",
    "SubredditResponse",
    "RedditPostResponse",
    "NewsResponse",
    # Status schemas
    "MonitoredSiteCreate",
    "MonitoredSiteUpdate",
    "MonitoredSiteResponse",
    "StatusCheckResponse",
    "SiteStatusSummary",
    "AllSitesStatusResponse",
]
