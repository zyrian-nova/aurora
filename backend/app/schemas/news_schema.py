"""
Schemas for news feeds (RSS and Reddit).
"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

# RSS feed schemas
class RSSFeedBase(BaseModel):
    """Base RSS feed schema."""
    url: HttpUrl
    title: Optional[str] = None

class RSSFeedCreate(RSSFeedBase):
    """Schema for creating RSS feed."""
    pass

class RSSFeedResponse(RSSFeedBase):
    """RSS feed response."""
    id: UUID
    description: Optional[str] = None
    site_url: Optional[HttpUrl] = None
    is_active: bool
    last_fetched_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RSSItemResponse(BaseModel):
    """Individual RSS feed item."""
    title: str
    link: HttpUrl
    description: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None

# Subreddit schemas
class SubredditBase(BaseModel):
    """Base subreddit schema."""
    name: str = Field(min_length=1, max_length=100)

class SubredditCreate(SubredditBase):
    """Schema for subscribing to subreddit."""
    pass

class SubredditResponse(SubredditBase):
    """Subreddit response."""
    id: UUID
    display_name: Optional[str] = None
    description: Optional[str] = None
    subscriber_count: Optional[int] = None
    is_nsfw: bool

    class Config:
        from_attributes = True

class RedditPostResponse(BaseModel):
    """Individual reddit post."""
    title: str
    author: str
    subreddit: str
    score: int
    num_comments: int
    url: HttpUrl
    permalink: str
    created_at: datetime
    is_ntfw: bool

# Aggregated news response
class NewsResponse(BaseModel):
    """Combined news from RSS and Reddit."""
    rss_items: list[RSSItemResponse] = Field(default_factory=list)
    reddit_posts: list[RedditPostResponse] = Field(default_factory=list)
    update_at: datetime
