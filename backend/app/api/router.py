"""
Main API router - Aggregates all route modules.
"""
from fastapi import APIRouter
from app.api.routes_auth import router as auth_router
from app.api.routes_user import router as user_router

# Main API router
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(auth_router)
api_router.include_router(user_router)

# Add here more routers as they get build
# api_router.include_router(daily_router)
