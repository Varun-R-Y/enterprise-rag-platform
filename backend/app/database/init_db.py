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
        from app.core.config import settings
        from app.core.security import get_password_hash
        from app.models.user import User, UserRole

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

        # Seed default admin user
        admin_email = settings.DEFAULT_ADMIN_EMAIL
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            logger.info(f"Seeding default admin user: {admin_email}...")
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                full_name="Default Admin",
                role=UserRole.ADMIN,
                tenant_id=default_tenant_id,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Success: Default admin seeded ({admin_email}).")
            logger.info(f"Default admin user {admin_email} seeded successfully.")

        # Seed default super admin user
        super_admin_email = settings.DEFAULT_SUPER_ADMIN_EMAIL
        if super_admin_email:
            super_admin_user = db.query(User).filter(User.email == super_admin_email).first()
            if not super_admin_user:
                logger.info(f"Seeding default super admin user: {super_admin_email}...")
                super_admin_user = User(
                    email=super_admin_email,
                    hashed_password=get_password_hash(settings.DEFAULT_SUPER_ADMIN_PASSWORD),
                    full_name="Default Super Admin",
                    role=UserRole.SUPER_ADMIN,
                    tenant_id=default_tenant_id,
                    is_active=True
                )
                db.add(super_admin_user)
                db.commit()
                print(f"Success: Default super admin seeded ({super_admin_email}).")
                logger.info(f"Default super admin user {super_admin_email} seeded successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding default database data: {e}")
    finally:
        db.close()
