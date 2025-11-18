from fastapi import FastAPI
from .database import engine
from . import models
from .routes import users, entries

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MindMate", description="AI-Powered Mental Wellness Journal")

# Include routers
app.include_router(users.router)
app.include_router(entries.router)

@app.get("/")
async def root():
    return {"message": "Welcome to MindMate API", "status": "running"}