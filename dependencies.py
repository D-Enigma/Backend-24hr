from database import SessionLocal


# Create a database session for each request and close it when the request is finished.
def get_db():
    db = SessionLocal()

    try:
        # FastAPI uses this session while handling the request.
        yield db
    finally:
        # Close the session even if something goes wrong during the request.
        db.close()
