from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from dependencies import get_db
from models import UserDB
from schemas import UserCreate, UserLogin
from security import create_access_token

# All authentication-related routes will start with /auth.
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Use the recommended password hashing algorithm instead of storing
# passwords directly in the database.
password_hash = PasswordHash.recommended()


@router.post("/register", status_code=201)
def register_user(u: UserCreate, db: Session = Depends(get_db)):
    # Check whether someone has already registered with this username.
    existing_user = db.query(UserDB).filter(UserDB.username == u.username).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    # Store the hashed password, not the original password.
    user = UserDB(username=u.username, hashed_password=password_hash.hash(u.password))

    db.add(user)
    db.commit()
    db.refresh(user)  # Get the new user's ID from the database.

    return {"id": user.id, "username": user.username}


@router.post("/login")
def login(u: UserLogin, db: Session = Depends(get_db)):
    # Find the account using the username provided during login.
    user = db.query(UserDB).filter(UserDB.username == u.username).first()

    # Use the same error message for both cases so we don't reveal
    # whether a particular username exists.
    if not user or not password_hash.verify(u.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Return a token that the client can use to access protected routes.
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}
