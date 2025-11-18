from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..AI import sentiment

router = APIRouter(prefix="/entries", tags=["entries"])

@router.post("/", response_model=schemas.JournalEntryResponse)
def create_entry(entry: schemas.JournalEntryCreate, db: Session = Depends(get_db)):
    # For now, using user_id=1. We'll add proper authentication later
    sentiment_result = sentiment.analyze_sentiment(entry.content)

    db_entry = models.JournalEntry(
        title=entry.title,
        content=entry.content,
        sentiment_score=sentiment_result["sentiment_score"],
        sentiment_label=sentiment_result["sentiment_label"],
        user_id=1  # Temporary - will replace with actual user ID from auth
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/", response_model=list[schemas.JournalEntryResponse])
def get_entries(db: Session = Depends(get_db)):
    entries = db.query(models.JournalEntry).filter(models.JournalEntry.user_id == 1).all()
    return entries