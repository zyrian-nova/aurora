"""
Backend entrypoint
"""
import random
import logging
import uvicorn
import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

# Logging start
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime(s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("aurora")


# Starting the app
app = FastAPI(
    title="Aurora API",
    description="Backend for the Aurora start page — weather, news, AI quotes, and more.",
    version="0.1.0",
)

# CORS config
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Endpoint to confirm start."""
    return {"message": "Welcome to Aurora 🌄", "status": "online"}

# Time Endpoint (EXAMPLE)
@app.get("/time")
async def get_time():
    """Return the current UTC and local time."""
    now = datetime.datetime.now()
    utc = datetime.datetime.now(datetime.UTC)
    return {
        "local_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "utc_time": utc.strftime("%Y-%m-%d %H:%M:%S %Z"),
    }

# Motivational phrase (EXAMPLE)
@app.get("/motivation")
async def get_motivation() -> dict[str,str]:
    """Return a daily motivational quote."""
    phrases = [
        "Keep your code clean and your mind clearer.",
        "Every sunrise is a new commit.",
        "Small steps lead to big releases.",
        "Trust the process — even async ones.",
        "Aurora rises — so can you.",
    ]
    return {"quote": random.choice(phrases)}

# Custom error handler
@app.exception_handler(404)
async def not_found(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=404, content={"error": "Endpoint not found"})

# Custom Exception handler
@app.exception_handler(Exception)
async def generic_error(request: Request, exc: Exception):
    # Full log
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    # Client response
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

# Start the server
if __name__ == "__main__":
    # Run uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
