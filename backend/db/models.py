from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    language = Column(String)
    location = Column(String)
    opt_in = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    type = Column(String)  # vaccination or outbreak
    message = Column(String)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String)  # pending, sent, failed

class VaccinationReminder(Base):
    __tablename__ = "vaccination_reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    child_age = Column(Float)
    vaccine_name = Column(String)
    due_date = Column(DateTime)
    reminded_at = Column(DateTime(timezone=True))

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_language = Column(String, default="en")  # Detected user language
    context = Column(JSON, default={})  # Store conversation context
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    message = Column(Text)
    response = Column(Text)
    intent = Column(String)
    confidence = Column(Float)
    language = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
