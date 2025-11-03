"""
User-related Pydantic schemas for request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)

class UserPrederencesSchema(BaseModel):
    """User preferences schema."""
    word_languages: list[str] = Field(default=["en", "es", "fi"])
    prefered_language: str = Field(default="en", max_length=10)
    theme: str = Field(default="auto", max_length=20)
    background_rotation: bool = True
    location: Optional[str] = Field(default=None, max_length=255)

    model_config = ConfigDict(from_attributes=True)

# Request schemas
