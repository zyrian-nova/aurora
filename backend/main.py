"""
Backend entrypoint for Aurora
"""
import os
import sys
import pytz
import time
import socket
import random
import uvicorn
import platform
from typing import Any, Dict
from tortoise import connections
from tortoise import Tortoise
from datetime import datetime
from contextlib import asynccontextmanager
from app.settings import settings, get_logger, setup_logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
# Routes
from app.api import api_router

# Saves the startup time of the app
START_TIME = time.time()

# Logging start
logger = setup_logging()

# Events (startup & shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Logs the app start and shutdown."""
    # Start
    logger.info("Aurora backend is starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1]}")

    # Initialize Tortoise ORM
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": [
            "app.models",
        ]}
    )
    if settings.ENVIRONMENT != "production":
        await Tortoise.generate_schemas()
    logger.info("Database initialized successfully")

    # Everything after this yield runs *after* the app starts
    yield

    # Shutdown
    logger.info("Closing database connections...")
    await Tortoise.close_connections()
    logger.info("Aurora backend is shutting down...")

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

# API router
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    """Endpoint to health check."""
    logger.debug("Root endpoint accessed")
    return {
        "status": "online",
        "message": "Welcome to Aurora 🌄"
    }

# Healthcheck endpoint for devs
@app.get("/health")
async def health() -> Dict[str, Any]:
    """Healthcheck with two levels: production and development."""
    hostname = None
    env = (settings.ENVIRONMENT or "").strip().lower()

    # Production mode or ENV variable empty
    if env in ("production", ""):
        logger.info("Healthy app: production")
        return {
            "status": "healthy",
            "message:": "Healthy app"
        }

    # Development / testing environments
    debug_envs = {"debug", "dev", "testing", "develop", "development"}

    if env in debug_envs:
        logger.info(f"App in debug mode: {env}")
        tz_name = getattr(settings, "APP_TIME_ZONE", "UTC")
        try:
            zone = pytz.timezone(tz_name)
            server_time = datetime.now(zone).isoformat()
        except Exception:
            server_time = datetime.now().isoformat()

        # Simple status from DB (without exposing sensible data)
        try:
            conn = connections.get("default")
            start = time.time()
            await conn.execute_query("SELECT 1")
            latency = round((time.time() - start) * 1000, 2)
            db_status = {"connected": True, "latency_ms": latency}
        except Exception:
            db_status = {"connected": False, "latency_ms": None}

        # Local IP
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            local_ip = "unknown"

        uptime_seconds = round(time.time() - START_TIME, 2)

        return {
            "app": {
                "title": app.title,
                "description": app.description,
                "version": app.version,
                "environment": env,
            },
            "server": {
                "hostname": hostname,
                "local_ip": local_ip,
                "python_version": platform.python_version(),
                "system": platform.system(),
                "release": platform.release(),
                "timezone": tz_name,
                "server_time": server_time,
                "process": {
                    "pid": os.getpid(),
                    "uptime": uptime_seconds,
                    "executable": sys.executable,
                },
            "database": db_status,
            }
        }

    # Unknowkn environment
    logger.warning(f"Environment variable not found or missing in .env file: {env}")
    return {
        "status": "Active",
        "message": "Unknowkn environment",
        "environment": env,
    }

# Checks if the proccess is still running
@app.get("/health/liveness", summary="Liveness probe")
async def liveness():
    return {"status": "ok"}

# Determines if the app is ready to recieve traffic
@app.get("/health/readiness", summary="Readiness probe")
async def readiness():
    try:
        # Fast ping to the DB (similar to SELECT 1)
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
        return {"status": "ready"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unready"}
        )

# Determines if the app has already finished its startup
@app.get("/health/startup", summary="Startup probe")
async def startup_probe():
    # Consider startup completed when lifespan reached the yield (which it did)
    return {"status": "started"}

# Time Endpoint (EXAMPLE)
@app.get("/time", response_model=dict[str, str])
async def get_time() -> dict[str, str]:
    """Return the current UTC and local time."""
    now = datetime.now()
    utc = datetime.now(datetime.UTC)

    logger.debug("Time endpoint accessed")

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
    logger.info(f"Serving motivation: {quote}")
    return {"quote": quote}

# Custom error handler
@app.exception_handler(404)
async def not_found(request: Request, exc: StarletteHTTPException):
    """Handle 404 errors."""
    logger.warning(f"404 Not Found: {request.url.path}")
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": request.url.path}
    )

# Custom Exception handler
@app.exception_handler(Exception)
async def generic_error(request: Request, exc: Exception):
    """Catch-all exception handler."""
    # Full log
    logger.error(
        f"Unhandled error on: {request.url.path}: {exc}",
        exc_info=True
    )
    # Don't leak internal errors in production
    if settings.ENVIRONMENT == "production":
        detail = "An internal error occurred"
    else:
        detail = repr(exc)

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
