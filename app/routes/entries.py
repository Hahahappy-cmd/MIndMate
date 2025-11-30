from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..AI import sentiment
from ..dependencies import get_current_user

router = APIRouter(prefix="/entries", tags=["entries"])

@router.post("/", response_model=schemas.JournalEntryResponse)
def create_entry(
    entry: schemas.JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Analyze sentiment
    sentiment_result = sentiment.analyze_sentiment(entry.content)
    
    # Create entry with current user
    db_entry = models.JournalEntry(
        title=entry.title,
        content=entry.content,
        sentiment_score=sentiment_result["sentiment_score"],
        sentiment_label=sentiment_result["sentiment_label"],
        user_id=current_user.id
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/", response_model=List[schemas.JournalEntryResponse])
def get_entries(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only return current user's entries
    entries = db.query(models.JournalEntry).filter(
        models.JournalEntry.user_id == current_user.id
    ).order_by(models.JournalEntry.created_at.desc()).all()
    return entries

@router.get("/{entry_id}", response_model=schemas.JournalEntryResponse)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == entry_id,
        models.JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    return entry

@router.put("/{entry_id}", response_model=schemas.JournalEntryResponse)
def update_entry(
    entry_id: int,
    entry_update: schemas.JournalEntryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == entry_id,
        models.JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    # Update fields if provided
    if entry_update.title is not None:
        entry.title = entry_update.title
    if entry_update.content is not None:
        entry.content = entry_update.content
        # Re-analyze sentiment if content changed
        sentiment_result = sentiment.analyze_sentiment(entry.content)
        entry.sentiment_score = sentiment_result["sentiment_score"]
        entry.sentiment_label = sentiment_result["sentiment_label"]
    
    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/{entry_id}")
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == entry_id,
        models.JournalEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted successfully"}