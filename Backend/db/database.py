# backend/db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read DB URL from env; default to sqlite file for local/dev
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./omr_results.db")

# SQLite needs check_same_thread False; other DBs ignore the argument
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    # Import models here so they are registered with Base.metadata
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

# Initialize DB tables on import (safe for dev; in production use migrations)
init_db()