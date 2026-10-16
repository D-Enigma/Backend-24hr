from fastapi import FastAPI

from database import Base, engine
from models import ComplaintDB
from routers.complaints import router
from routers.auth import router as auth_router

# Create the FastAPI application.
app = FastAPI()

# Register the authentication endpoints, such as user registration and login.
app.include_router(auth_router)

# Create the database tables if they don't already exist.
Base.metadata.create_all(bind=engine)

# Register the endpoints for creating and managing complaints.
app.include_router(router)


# A simple endpoint to check whether the API is running.
@app.get("/")
def home():
    return {"message": "24HR Backend is LIVE!"}
