from sqlalchemy import create_engine
from app.core.config import settings

if settings.DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set.")

# Sync SQLAlchemy Engine for PostgreSQL database operations
engine = create_engine(
    url=settings.DATABASE_URL,
    pool_pre_ping=True,  # Disconnects stale/dead connections and refreshes them transparently
)
