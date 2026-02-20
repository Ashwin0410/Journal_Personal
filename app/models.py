from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    entries = relationship("Entry", back_populates="user", cascade="all, delete-orphan")


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entry_type = Column(String(50), nullable=False)  # text, image, voice, video, task, gratitude
    content = Column(Text, nullable=True)  # text content or caption
    media_base64 = Column(Text, nullable=True)  # base64 encoded media
    media_mime = Column(String(100), nullable=True)  # e.g., image/jpeg, audio/webm
    is_completed = Column(Boolean, default=False)  # for tasks
    mood = Column(String(50), nullable=True)  # optional mood tag
    entry_date = Column(Date, nullable=False)  # the journal date this belongs to
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="entries")
