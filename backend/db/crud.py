from sqlalchemy.orm import Session
from . import models

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def create_user(db: Session, phone: str, language: str, location: str):
    db_user = models.User(phone=phone, language=language, location=location)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_alert(db: Session, user_id: int, alert_type: str, message: str):
    db_alert = models.Alert(user_id=user_id, type=alert_type, message=message, status="pending")
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def create_vaccination_reminder(db: Session, user_id: int, child_age: float, vaccine_name: str, due_date: str):
    db_reminder = models.VaccinationReminder(
        user_id=user_id,
        child_age=child_age,
        vaccine_name=vaccine_name,
        due_date=due_date
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder