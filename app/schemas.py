from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


# --- Auth ---
class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Entries ---
class EntryCreate(BaseModel):
    entry_type: str  # text, image, voice, video, task, gratitude
    content: Optional[str] = None
    media_base64: Optional[str] = None
    media_mime: Optional[str] = None
    is_completed: Optional[bool] = False
    mood: Optional[str] = None
    entry_date: date


class EntryUpdate(BaseModel):
    content: Optional[str] = None
    is_completed: Optional[bool] = None
    mood: Optional[str] = None


class EntryResponse(BaseModel):
    id: int
    user_id: int
    entry_type: str
    content: Optional[str]
    media_base64: Optional[str]
    media_mime: Optional[str]
    is_completed: bool
    mood: Optional[str]
    entry_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
