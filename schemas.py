from enum import Enum

from pydantic import BaseModel, Field


# Keep complaint statuses consistent across requests and responses.
class ComplaintStatus(str, Enum):
    pending = "Pending"
    in_progress = "In Progress"
    resolved = "Resolved"


# Fields required when a user submits a new complaint.
class ComplaintCreate(BaseModel):
    title: str
    description: str
    location: str


# Controls which complaint details are returned by the API.
class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    status: ComplaintStatus

    # Allow Pydantic to read these values directly from SQLAlchemy model objects.
    model_config = {"from_attributes": True}


# Only the status can be changed through the complaint update endpoint.
class ComplaintUpdate(BaseModel):
    status: ComplaintStatus


# Validate registration details before creating a new account.
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)


# Fields required when a user logs in.
class UserLogin(BaseModel):
    username: str
    password: str
