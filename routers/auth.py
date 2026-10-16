from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# from database import SessionLocal
from dependencies import get_db
from models import UserDB
from schemas import UserCreate

from fastapi.security import OAuth2PasswordRequestForm
from security import create_access_token
from schemas import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])

password_hash = PasswordHash.recommended()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@router.post("/register", status_code=201)
def register_user(u: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.username == u.username).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = UserDB(username=u.username, hashed_password=password_hash.hash(u.password))

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "username": user.username}


@router.post("/login")
def login(u: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == u.username).first()

    if not user or not password_hash.verify(u.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"access_token": create_access_token(user.username), "token_type": "bearer"}
