"""
User-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from uuid import UUID
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
class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(min_length=8, max_length=50)
    full_name: Optional[str] = Field(default=None, min_length=3, max_length=255)

class UserUpdate(BaseModel):
    """Schema for update user profile."""
    full_name: Optional[str] = Field(default=None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=64)

    model_config = ConfigDict(from_attributes=True)

class PasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str = Field(min_length=3, max_length=64)
    new_password: str = Field(min_length=3, max_length=64)

class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    word_languages: Optional[list[str]] = None
    prefered_language: Optional[str] = Field(default=None, max_length=10)
    theme: Optional[str] = Field(default=None, max_length=20)
    background_rotation: Optional[bool] = None
    location: Optional[str] = Field(default=None, max_length=255)

# Response schemas
class UserResponse(UserBase):
    """Schema for user response (excludes password)."""
    id: UUID
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserWithPreferences(UserResponse):
    """User response with preferences included."""
    preferences: Optional[UserPrederencesSchema] = None

    model_config = ConfigDict(from_attributes=True)
