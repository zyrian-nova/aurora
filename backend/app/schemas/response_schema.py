"""
General response schemas for API endponits.
"""
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

# Generic type for data
DataT = TypeVar("DataT")

# Success Responses
class SuccessResponse(BaseModel, Generic[DataT]):
    """Generic success response wrapper."""
    success: bool = True
    message: str
    data: Optional[DataT] = None

class MessageResponse(BaseModel):
    """Simple message response."""
    message: str

# Error Responses
class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    field: str
    message: str

class ValidationErrorResponse(BaseModel):
    """Validation error response with field details."""
    success: bool = False
    error: str = "Validation error"
    details: list[ValidationErrorDetail]

# Paginated Responses
class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_pages: int = Field(ge=0)
    total_items: int = Field(ge=0)
    has_next: bool
    has_previous: bool

class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated response."""
    success: bool = True
    data: list[DataT]
    meta: PaginationMeta
