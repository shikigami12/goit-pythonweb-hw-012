from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date, timedelta
from .auth import get_password_hash
import uuid


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    verification_token = str(uuid.uuid4())
    db_user = models.User(email=user.email, hashed_password=hashed_password,
                          verification_token=verification_token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_verification_status(db: Session, user: models.User):
    user.verified = True
    user.verification_token = None
    db.commit()
    return user


def set_verification_token(db: Session, user: models.User):
    verification_token = str(uuid.uuid4())
    user.verification_token = verification_token
    db.commit()
    return user


def update_avatar(db: Session, user: models.User, url: str):
    user.avatar = url
    db.commit()
    return user


def get_contact(db: Session, contact_id: int, user_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id,
                                           models.Contact.user_id == user_id).first()


def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(
        models.Contact.user_id == user_id).offset(skip).limit(limit).all()


def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    db_contact = models.Contact(**contact.dict(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: schemas.ContactCreate,
                   user_id: int):
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id, models.Contact.user_id == user_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    db_contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id, models.Contact.user_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def search_contacts(db: Session, query: str, user_id: int):
    return db.query(models.Contact).filter(
        (models.Contact.first_name.ilike(f"%{query}%")) |
        (models.Contact.last_name.ilike(f"%{query}%")) |
        (models.Contact.email.ilike(f"%{query}%")),
        models.Contact.user_id == user_id
    ).all()


def get_birthdays(db: Session, user_id: int):
    today = date.today()
    end_date = today + timedelta(days=7)
    return db.query(models.Contact).filter(
        (models.Contact.birthday >= today) &
        (models.Contact.birthday <= end_date),
        models.Contact.user_id == user_id
    ).all()