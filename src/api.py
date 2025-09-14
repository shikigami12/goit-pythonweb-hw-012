from fastapi import (
    APIRouter, Depends, HTTPException, status, Request, UploadFile, File
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, models, schemas, auth, cloudinary_utils
from .database import SessionLocal, engine
from datetime import timedelta
from .main import limiter

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup", response_model=schemas.User,
             status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = crud.create_user(db=db, user=user)
    # In a real app, you would send an email with the verification link
    print(f"Verification token for {new_user.email}: "
          f"{new_user.verification_token}")
    return new_user


@router.get("/verifyemail/{token}", response_model=schemas.User)
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.verification_token == token).first()
    if user is None:
        raise HTTPException(status_code=404,
                            detail="User not found or already verified")
    crud.update_verification_status(db, user)
    return user


@router.post("/resend-verification-email/")
def resend_verification_email(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.verified:
        raise HTTPException(status_code=400, detail="User already verified")
    crud.set_verification_token(db, user)
    # In a real app, you would send an email with the verification link
    print(f"Verification token for {user.email}: {user.verification_token}")
    return {"message": "Verification email resent"}


@router.post("/login", response_model=schemas.Token)
def login(db: Session = Depends(get_db),
          form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password,
                                           user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.verified:
        raise HTTPException(status_code=401,
                            detail="Please verify your email address")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=schemas.User)
@limiter.limit("10/minute")
async def read_users_me(request: Request,
                      current_user: models.User = Depends(
                          auth.get_current_user)):
    return current_user


@router.patch("/users/avatar", response_model=schemas.User)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    url = cloudinary_utils.upload_avatar(
        file.file, f"avatars/{current_user.id}")
    user = crud.update_avatar(db, current_user, url)
    return user


@router.post("/contacts/", response_model=schemas.Contact,
             status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)


@router.get("/contacts/", response_model=list[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  current_user: models.User = Depends(auth.get_current_user)):
    contacts = crud.get_contacts(
        db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts


@router.get("/contacts/search", response_model=list[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db),
                    current_user: models.User = Depends(auth.get_current_user)):
    contacts = crud.search_contacts(db, query=query, user_id=current_user.id)
    return contacts


@router.get("/contacts/birthdays", response_model=list[schemas.Contact])
def get_birthdays(db: Session = Depends(get_db),
                  current_user: models.User = Depends(auth.get_current_user)):
    contacts = crud.get_birthdays(db, user_id=current_user.id)
    return contacts


@router.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    db_contact = crud.get_contact(
        db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    db_contact = crud.update_contact(
        db, contact_id=contact_id, contact=contact, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    db_contact = crud.delete_contact(
        db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact