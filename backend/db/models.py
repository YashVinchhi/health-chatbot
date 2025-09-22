from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

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