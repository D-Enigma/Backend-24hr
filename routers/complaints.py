from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from models import ComplaintDB
from schemas import ComplaintCreate, ComplaintResponse, ComplaintUpdate
from security import get_current_user

from logging_config import logger

router = APIRouter(prefix="/complaints", tags=["Complaints"])


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# Create a complaint
@router.post("", response_model=ComplaintResponse, status_code=201)
def create_complaint(
    c: ComplaintCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    try:
        new_complaint = ComplaintDB(
            title=c.title,
            description=c.description,
            location=c.location,
            user_id=user.id,
        )

        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)

        logger.info("Complaint created: id=%s user_id=%s", new_complaint.id, user.id)

        return new_complaint

    except Exception:
        db.rollback()
        logger.exception("Failed to create complaint for user_id=%s", user.id)
        raise HTTPException(status_code=500, detail="Unable to create complaint")


# Get all complaints
@router.get("", response_model=list[ComplaintResponse])
def get_complaints(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(ComplaintDB).filter(ComplaintDB.user_id == user.id).all()


# Get a specific complaint
@router.get("/{id}", response_model=ComplaintResponse)
def get_complaint(
    id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    c = (
        db.query(ComplaintDB)
        .filter(ComplaintDB.id == id, ComplaintDB.user_id == user.id)
        .first()
    )

    if c is None:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return c


# Update complaint status
@router.patch("/{id}", response_model=ComplaintResponse)
def update_complaint(
    id: int,
    c: ComplaintUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    x = (
        db.query(ComplaintDB)
        .filter(ComplaintDB.id == id, ComplaintDB.user_id == user.id)
        .first()
    )

    if x is None:
        raise HTTPException(status_code=404, detail="Complaint not found")

    x.status = c.status

    db.commit()
    db.refresh(x)

    return x


# Delete a complaint
@router.delete("/{id}", status_code=204)
def delete_complaint(
    id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    c = (
        db.query(ComplaintDB)
        .filter(ComplaintDB.id == id, ComplaintDB.user_id == user.id)
        .first()
    )

    if c is None:
        raise HTTPException(status_code=404, detail="Complaint not found")

    db.delete(c)
    db.commit()
