"""Database connection and session management"""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from tracker.config import settings

# Base class for all ORM models
Base = declarative_base()


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite"""
    if "sqlite" in str(dbapi_conn):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@event.listens_for(Engine, "connect")
def enable_wal_mode(dbapi_conn, connection_record):
    """Enable WAL mode for better concurrent access"""
    if "sqlite" in str(dbapi_conn):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


def get_engine():
    """Create and configure SQLAlchemy engine"""
    # Resolve database path
    db_path = settings.get_database_path()

    # Create parent directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create engine
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # Allow multi-threaded access
        echo=False,  # Set to True for SQL logging
    )

    return engine


# Create engine and session factory
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session (dependency injection for FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database schema"""
    # Import all models to register them
    from tracker.core import models  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)


def reset_db():
    """Drop and recreate all tables (WARNING: deletes all data)"""
    # Import all models to register them
    from tracker.core import models  # noqa: F401

    # Drop all tables
    Base.metadata.drop_all(bind=engine)

    # Recreate all tables
    Base.metadata.create_all(bind=engine)
