
"""
=========================================================
MUGONEXT
Database Configuration
=========================================================
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session for FastAPI dependencies.

    The session is closed after the request finishes, even if
    an exception occurs.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
