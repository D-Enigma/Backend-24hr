import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Read the database URL from the environment; use a local SQLite database by default.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./complaints.db")

# Create the database connection.
# This setting allows SQLite to be used across FastAPI's threads.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create database sessions that our endpoints can use to read and write data.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the database models defined in models.py.
Base = declarative_base()
