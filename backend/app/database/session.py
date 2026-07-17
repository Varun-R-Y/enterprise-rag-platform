from typing import Generator
from sqlalchemy.orm import sessionmaker, Session

from app.database.connection import engine

# Sync Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Dependency to get database sessions (FastAPI dependency injection)
def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator for database session.
    Ensures that the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
