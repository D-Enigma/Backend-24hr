from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from models import ComplaintDB
from schemas import ComplaintCreate, ComplaintResponse, ComplaintUpdate
from security import get_current_user
from logging_config import logger

# All complaint-related endpoints will start with /complaints.
router = APIRouter(prefix="/complaints", tags=["Complaints"])


# Create a new complaint for the currently logged-in user.
@router.post("", response_model=ComplaintResponse, status_code=201)
def create_complaint(
    c: ComplaintCreate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    try:
        # Save the complaint along with the ID of the user who created it.
        new_complaint = ComplaintDB(
            title=c.title,
            description=c.description,
            location=c.location,
            user_id=user.id,
        )

        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)  # Load the ID and other database-generated values.

        logger.info("Complaint created: id=%s user_id=%s", new_complaint.id, user.id)

        return new_complaint

    except Exception:
        # Undo any unfinished database changes if something goes wrong.
        db.rollback()
        logger.exception("Failed to create complaint for user_id=%s", user.id)
        raise HTTPException(status_code=500, detail="Unable to create complaint")


# Return only the complaints belonging to the logged-in user.
@router.get("", response_model=list[ComplaintResponse])
def get_complaints(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(ComplaintDB).filter(ComplaintDB.user_id == user.id).all()


# Find one complaint by its ID, but only if it belongs to the current user.
@router.get("/{id}", response_model=ComplaintResponse)
def get_complaint(
    id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    c = (
        db.query(ComplaintDB)
        .filter(ComplaintDB.id == id, ComplaintDB.user_id == user.id)
        .first()
    )

    # Return the same response if the complaint doesn't exist or belongs to someone else.
    if c is None:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return c


# Update the status of one of the user's complaints.
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

    # Apply the new status and save the change to the database.
    x.status = c.status

    db.commit()
    db.refresh(x)

    return x


# Permanently delete a complaint belonging to the logged-in user.
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
