from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class ComplaintDB(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Pending")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)


status = Column(String, nullable=False, default="Pending")
