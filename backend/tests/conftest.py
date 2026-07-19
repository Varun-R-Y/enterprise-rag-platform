import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from main import app

# Use in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture() -> Generator[Session, None, None]:
    """
    Creates a new database session for a test, with tables created, seeded, and dropped.
    """
    Base.metadata.create_all(bind=engine)
    
    # Seed default tenant and admin user in the testing database
    import uuid
    from app.models.tenant import Tenant
    from app.models.user import User, UserRole
    from app.core.config import settings
    from app.core.security import get_password_hash

    db_seed = TestingSessionLocal()
    try:
        default_tenant_id = uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
        tenant = db_seed.query(Tenant).filter(Tenant.id == default_tenant_id).first()
        if not tenant:
            tenant = Tenant(id=default_tenant_id, name="Default Tenant", slug="default")
            db_seed.add(tenant)
            db_seed.commit()

        admin_email = settings.DEFAULT_ADMIN_EMAIL
        admin_user = db_seed.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                full_name="Default Admin",
                role=UserRole.ADMIN,
                tenant_id=default_tenant_id,
                is_active=True
            )
            db_seed.add(admin_user)
            db_seed.commit()

        super_admin_email = "superadmin@saas.com"
        super_admin_user = db_seed.query(User).filter(User.email == super_admin_email).first()
        if not super_admin_user:
            super_admin_user = User(
                email=super_admin_email,
                hashed_password=get_password_hash("superadminpass123"),
                full_name="Default Super Admin",
                role=UserRole.SUPER_ADMIN,
                tenant_id=default_tenant_id,
                is_active=True
            )
            db_seed.add(super_admin_user)
            db_seed.commit()
    finally:
        db_seed.close()

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(db_session: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI test client with database dependency override.
    """
    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
