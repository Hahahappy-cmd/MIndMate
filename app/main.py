from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routes import users, entries
from datetime import timezone, datetime
# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MindMate",
    description="AI-Powered Mental Wellness Journal with Advanced Emotion Analysis",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(entries.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to MindMate API",
        "version": "4.0.0",
        "status": "running",
        "features": [
            "User authentication with JWT & refresh tokens",
            "Password reset functionality",
            "Journal entries with AI sentiment analysis",
            "Advanced emotion detection (8 emotions)",
            "Weekly AI summaries",
            "Emotion trend analysis",
            "Full CRUD operations"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)