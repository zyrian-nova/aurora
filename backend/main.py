"""
Backend entrypoint for Aurora
"""
import random
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager
from app.settings import settings, setup_logging, get_logger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# Logging start
logger = setup_logging()
app_logger = get_logger(__name__)

# Events (startup & shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Logs the app start and shutdown."""
    # Start
    app_logger.info("Aurora backend is starting up...")
    app_logger.info(f"Environment: {settings.ENVIRONMENT}")
    app_logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1]}")

    # Everything after this yield runs *after* the app starts
    yield

    # Shutdown
    app_logger.info("Aurora backend is shutting down...")

# Starting the app
app = FastAPI(
    title="Aurora API",
    description="Backend for the Aurora start page — weather, news, AI quotes, and more.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Endpoint to health check."""
    app_logger.debug("Root endpoint accessed")
    return {
        "message": "Welcome to Aurora 🌄",
        "status": "online",
        "version": app.version
    }

# Time Endpoint (EXAMPLE)
@app.get("/time", response_model=dict[str, str])
async def get_time() -> dict[str, str]:
    """Return the current UTC and local time."""
    now = datetime.now()
    utc = datetime.now(datetime.UTC)

    app_logger.debug("Time endpoint accessed")

    return {
        "local_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "utc_time": utc.strftime("%Y-%m-%d %H:%M:%S %Z"),
    }

# Motivational phrase (EXAMPLE)
@app.get("/motivation", response_model=dict[str, str])
async def get_motivation() -> dict[str,str]:
    """Return a daily motivational quote."""
    phrases = [
        "Keep your code clean and your mind clearer.",
        "Every sunrise is a new commit.",
        "Small steps lead to big releases.",
        "Trust the process — even async ones.",
        "Aurora rises — so can you.",
    ]

    quote = random.choice(phrases)
    app_logger.info(f"Serving motivation: {quote}")
    return {"quote": quote}

# Custom error handler
@app.exception_handler(404)
async def not_found(request: Request, exc: StarletteHTTPException):
    """Handle 404 errors."""
    app_logger.warning(f"404 Not Found: {request.url.path}")
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": request.url.path}
    )

# Custom Exception handler
@app.exception_handler(Exception)
async def generic_error(request: Request, exc: Exception):
    """Catch-all exception handler."""
    # Full log
    app_logger.error(
        f"Unhandled error on: {request.url.path}: {exc}",
        exc_info=True
    )
    # Don't leak internal errors in production
    if settings.ENVIRONMENT == "production":
        detail = "An internal error occurred"
    else:
        detail = str(exc)

    # Client response
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": detail
        }
    )

# Start the server
if __name__ == "__main__":
    # Run uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
