import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use the established SQLite database file
# This points directly to backend/titancare.db since it runs from backend folder
DB_URL = "sqlite:///./titancare.db"

# connect_args={"check_same_thread": False} is required for SQLite and FastAPI async contexts
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy Models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
