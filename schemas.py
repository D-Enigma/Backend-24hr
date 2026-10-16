from enum import Enum

from pydantic import BaseModel, Field


class ComplaintStatus(str, Enum):
    pending = "Pending"
    in_progress = "In Progress"
    resolved = "Resolved"


class ComplaintCreate(BaseModel):
    title: str
    description: str
    location: str


class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    status: ComplaintStatus

    model_config = {"from_attributes": True}


class ComplaintUpdate(BaseModel):
    status: ComplaintStatus


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str
