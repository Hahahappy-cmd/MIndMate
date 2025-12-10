from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional, List

# Password constraints: at least 8 characters
PasswordStr = constr(min_length=8)

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

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: PasswordStr

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

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class UserWithEntries(UserResponse):
    entries: List[JournalEntryResponse] = []