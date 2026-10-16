import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from models import UserDB


# Read the secret from the environment instead of keeping it in the code.
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

# Stop the application from starting if the secret hasn't been configured.
if not SECRET_KEY:
    raise RuntimeError("Set the JWT_SECRET_KEY environment variable")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Create a token after a user successfully logs in.
def create_access_token(username: str):
    now = datetime.now(timezone.utc)

    # Store the username and timestamps inside the token.
    # The expiration time prevents the token from remaining valid forever.
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Read the bearer token sent in the Authorization header.
bearer = HTTPBearer()


# Check the token and identify the user making the request.
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials

    try:
        # Decode the token to verify its signature and expiration time.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

    except jwt.InvalidTokenError:
        # Reject tokens that are invalid or have expired.
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Look up the account associated with the username in the token.
    db = SessionLocal()

    try:
        user = db.query(UserDB).filter(UserDB.username == username).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    finally:
        # Close the database session after retrieving the user.
        db.close()
