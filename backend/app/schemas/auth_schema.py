"""
Authentication-related Pydantic schemas.
"""
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

# Request schemas
class LoginRequest(BaseModel):
    """Schema for login credentials."""
    email: EmailStr
    password: str = Field(min_length=1)

class RefreshTokenRequest(BaseModel):
    """Schema for token refresh."""
    refres_token: str = Field(min_length=1)

# Response schemas
class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayloadResponse(BaseModel):
    """Token payload information (for debbuging)."""
    user_id: UUID
    username: str
    token_type: str
    expires_at: float
