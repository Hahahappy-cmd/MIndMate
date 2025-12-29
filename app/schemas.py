from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional, List, Dict, Any

# Password constraints: at least 8 characters
PasswordStr = constr(min_length=8)

# === User Schemas ===
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: PasswordStr

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# === Token Schemas ===
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None

# === Password Reset Schemas ===
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: PasswordStr

# === Journal Entry Schemas ===
class JournalEntryBase(BaseModel):
    title: str
    content: str

class JournalEntryCreate(JournalEntryBase):
    pass

class JournalEntryResponse(JournalEntryBase):
    id: int
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    created_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True

# === Enhanced Journal Entry Schemas (Week 4) ===
class EmotionData(BaseModel):
    joy: float = 0
    sadness: float = 0
    anger: float = 0
    fear: float = 0
    surprise: float = 0
    trust: float = 0
    anticipation: float = 0
    disgust: float = 0

class JournalEntryEnhanced(JournalEntryResponse):
    subjectivity: Optional[float] = None
    word_count: Optional[int] = None
    emotion_data: Optional[EmotionData] = None
    key_phrases: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# === User with Entries ===
class UserWithEntries(UserResponse):
    entries: List[JournalEntryResponse] = []

# === AI Feature Schemas (Week 4) ===
class WeeklySummary(BaseModel):
    summary: str
    statistics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]

class EmotionTrends(BaseModel):
    period_days: int
    total_entries: int
    trend_analysis: Dict[str, Any]
    entries: List[Dict[str, Any]]