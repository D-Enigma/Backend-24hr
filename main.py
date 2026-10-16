from fastapi import FastAPI

from database import Base, engine
from models import ComplaintDB
from routers.complaints import router

from routers.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router)

Base.metadata.create_all(bind=engine)

app.include_router(router)


@app.get("/")
def home():
    return {"message": "24HR Backend is LIVE!"}
