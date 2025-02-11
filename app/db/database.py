from typing import Annotated
import os
from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from sqlmodel import (
    create_engine,
    SQLModel,
    Session,
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mydatabase")

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

# Make a session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
)

def get_session():
    """
    FastAPI dependency that provides a SQLModel session.
    Each request gets its own session, which is closed on exit.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# For type-annotated dependencies in your routes
SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    """
    Creates tables for all SQLModel metadata if they don't already exist.
    Call this at startup (or whenever you need) to ensure DB is set up.
    """
    SQLModel.metadata.create_all(engine)
