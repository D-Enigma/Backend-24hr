from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


# This model represents the complaints stored in the database.
class ComplaintDB(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)

    # New complaints start as pending until their status is updated.
    status = Column(String, nullable=False, default="Pending")

    # Link each complaint to the user who created it.
    # Nullable allows older complaints without an assigned user to remain valid.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


# This model stores the registered users and their login credentials.
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Each user must have a unique username.
    username = Column(String, unique=True, nullable=False, index=True)

    # Store the hashed password instead of the original password.
    hashed_password = Column(String, nullable=False)
