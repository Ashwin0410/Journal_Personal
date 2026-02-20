import os
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import extract

from app.database import engine, get_db, Base
from app.models import User, Entry
from app.schemas import (
    UserRegister, UserLogin, UserResponse, TokenResponse,
    EntryCreate, EntryUpdate, EntryResponse,
)
from app.auth import hash_password, verify_password, create_access_token, get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Journal", version="1.0.0")

# --- Static files ---
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ==================== AUTH ====================

@app.post("/api/auth/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@app.post("/api/auth/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@app.get("/api/auth/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


# ==================== ENTRIES ====================

@app.post("/api/entries", response_model=EntryResponse)
def create_entry(data: EntryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = Entry(
        user_id=user.id,
        entry_type=data.entry_type,
        content=data.content,
        media_base64=data.media_base64,
        media_mime=data.media_mime,
        is_completed=data.is_completed or False,
        mood=data.mood,
        entry_date=data.entry_date,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return EntryResponse.model_validate(entry)


@app.get("/api/entries", response_model=List[EntryResponse])
def get_entries(
    entry_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Entry).filter(Entry.user_id == user.id)
    if entry_date:
        q = q.filter(Entry.entry_date == entry_date)
    return [EntryResponse.model_validate(e) for e in q.order_by(Entry.created_at.asc()).all()]


@app.get("/api/entries/range", response_model=List[EntryResponse])
def get_entries_range(
    start: date = Query(...),
    end: date = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entries = (
        db.query(Entry)
        .filter(Entry.user_id == user.id, Entry.entry_date >= start, Entry.entry_date <= end)
        .order_by(Entry.entry_date.asc(), Entry.created_at.asc())
        .all()
    )
    return [EntryResponse.model_validate(e) for e in entries]


@app.get("/api/entries/on-this-day", response_model=List[EntryResponse])
def on_this_day(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = date.today()
    entries = (
        db.query(Entry)
        .filter(
            Entry.user_id == user.id,
            extract("month", Entry.entry_date) == today.month,
            extract("day", Entry.entry_date) == today.day,
            Entry.entry_date != today,
        )
        .order_by(Entry.entry_date.desc())
        .all()
    )
    return [EntryResponse.model_validate(e) for e in entries]


@app.get("/api/entries/dates-with-entries")
def dates_with_entries(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entries = (
        db.query(Entry.entry_date)
        .filter(
            Entry.user_id == user.id,
            extract("month", Entry.entry_date) == month,
            extract("year", Entry.entry_date) == year,
        )
        .distinct()
        .all()
    )
    return [e[0].isoformat() for e in entries]


@app.put("/api/entries/{entry_id}", response_model=EntryResponse)
def update_entry(
    entry_id: int,
    data: EntryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if data.content is not None:
        entry.content = data.content
    if data.is_completed is not None:
        entry.is_completed = data.is_completed
    if data.mood is not None:
        entry.mood = data.mood
    db.commit()
    db.refresh(entry)
    return EntryResponse.model_validate(entry)


@app.delete("/api/entries/{entry_id}")
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"ok": True}


# ==================== CATCH-ALL: serve frontend ====================

@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    return FileResponse(os.path.join(static_dir, "index.html"))
