from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime, timedelta, timezone
from ..database import get_db
from .. import models, schemas
from ..AI import sentiment, summarizer
from ..dependencies import get_current_user

router = APIRouter(prefix="/entries", tags=["entries"])

# ========== CREATE ==========
@router.post("/", response_model=schemas.JournalEntryResponse)
def create_entry(
    entry: schemas.JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Enhanced sentiment analysis
    sentiment_result = sentiment.analyze_sentiment_advanced(entry.content)
    
    # Create entry with enhanced data
    db_entry = models.JournalEntry(
        title=entry.title,
        content=entry.content,
        sentiment_score=sentiment_result["sentiment_score"],
        sentiment_label=sentiment_result["sentiment_label"],
        subjectivity=sentiment_result.get("subjectivity"),
        word_count=sentiment_result.get("word_count"),
        emotion_data=json.dumps(sentiment_result.get("emotions", {})),
        key_phrases=json.dumps(sentiment_result.get("key_phrases", [])),
        user_id=current_user.id
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# ========== READ ALL ==========
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

# ========== READ SINGLE ==========
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

# ========== UPDATE ==========
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
        sentiment_result = sentiment.analyze_sentiment_advanced(entry.content)
        entry.sentiment_score = sentiment_result["sentiment_score"]
        entry.sentiment_label = sentiment_result["sentiment_label"]
        entry.subjectivity = sentiment_result.get("subjectivity")
        entry.word_count = sentiment_result.get("word_count")
        entry.emotion_data = json.dumps(sentiment_result.get("emotions", {}))
        entry.key_phrases = json.dumps(sentiment_result.get("key_phrases", []))
    
    db.commit()
    db.refresh(entry)
    return entry

# ========== DELETE ==========
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

# ========== WEEK 4 AI FEATURES ==========

@router.get("/weekly-summary", response_model=schemas.WeeklySummary)
def get_weekly_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get AI-generated weekly summary"""
    # Get entries from last week
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    entries = db.query(models.JournalEntry).filter(
        models.JournalEntry.user_id == current_user.id,
        models.JournalEntry.created_at >= one_week_ago
    ).order_by(models.JournalEntry.created_at).all()
    
    # Convert to dict format for summarizer
    entries_data = []
    for entry in entries:
        entry_dict = {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "sentiment_score": entry.sentiment_score,
            "sentiment_label": entry.sentiment_label,
            "subjectivity": entry.subjectivity,
            "word_count": entry.word_count,
            "emotion_data": entry.emotion_data,
            "created_at": entry.created_at.isoformat() if entry.created_at else None
        }
        entries_data.append(entry_dict)
    
    # Generate summary
    summary = summarizer.generate_weekly_summary(entries_data)
    
    return summary

@router.get("/emotion-trends", response_model=schemas.EmotionTrends)
def get_emotion_trends(
    days: int = 30,  # Default to 30 days
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get emotion trends over time"""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    entries = db.query(models.JournalEntry).filter(
        models.JournalEntry.user_id == current_user.id,
        models.JournalEntry.created_at >= start_date
    ).order_by(models.JournalEntry.created_at).all()
    
    # Prepare data for trend analysis
    entries_data = []
    for entry in entries:
        emotions = {}
        if entry.emotion_data:
            try:
                emotions = json.loads(entry.emotion_data)
            except:
                pass
        
        entry_dict = {
            "sentiment_score": entry.sentiment_score,
            "sentiment_label": entry.sentiment_label,
            "emotions": emotions,
            "created_at": entry.created_at
        }
        entries_data.append(entry_dict)
    
    # Analyze trends
    trends = sentiment.analyze_emotion_trends(entries_data)
    
    return {
        "period_days": days,
        "total_entries": len(entries),
        "trend_analysis": trends,
        "entries": [
            {
                "date": e.created_at.isoformat() if e.created_at else None,
                "sentiment": e.sentiment_score,
                "label": e.sentiment_label
            }
            for e in entries[-10:]  # Last 10 entries for chart
        ]
    }