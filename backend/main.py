"""
Backend entrypoint
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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
    # Endpoint to confirm start
    return {"message": "Welcome to Aurora 🌄", "status": "online"}

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
