import logging
from app.database.base import Base
from app.database.connection import engine

# Import all models to ensure they are registered on Base.metadata before create_all is called
from app.models.tenant import Tenant
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation
from app.models.message import Message

logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Initializes the database schema by creating all registered tables.
    """
    logger.info("Initializing database tables...")
    
    # Creates all tables registered on Base metadata
    Base.metadata.create_all(bind=engine)
    
    print("Success: Database tables created successfully.")
    logger.info("Database tables created successfully.")

    # Seed default tenant so registration works out of the box
    from app.database.session import SessionLocal
    import uuid
    
    db = SessionLocal()
    try:
        default_tenant_id = uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
        tenant = db.query(Tenant).filter(Tenant.id == default_tenant_id).first()
        if not tenant:
            logger.info("Seeding default tenant...")
            tenant = Tenant(
                id=default_tenant_id,
                name="Default Tenant",
                slug="default"
            )
            db.add(tenant)
            db.commit()
            print("Success: Default tenant seeded.")
            logger.info("Default tenant seeded successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding default tenant: {e}")
    finally:
        db.close()
