import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.deps import require_super_admin, require_admin_or_super_admin
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantOut, TenantDetailsOut, TenantListResponse
from app.services.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post("", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
def create_company(
    schema: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
) -> TenantOut:
    """
    Creates a new company (tenant). Super Admin only.
    """
    return TenantService.create_tenant(db, schema)

@router.get("", response_model=List[TenantListResponse])
def list_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
) -> List[TenantListResponse]:
    """
    Lists all companies with their associated admin emails and stats. Super Admin only.
    """
    return TenantService.list_tenants(db)

@router.get("/{tenant_id}", response_model=TenantDetailsOut)
def get_company(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
) -> TenantDetailsOut:
    """
    Retrieves company details along with analytics stats. Super Admin only.
    """
    return TenantService.get_tenant_details(db, tenant_id)

@router.patch("/{tenant_id}", response_model=TenantOut)
def update_company(
    tenant_id: uuid.UUID,
    schema: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
) -> TenantOut:
    """
    Updates company settings or toggles active state. Super Admin only.
    """
    return TenantService.update_tenant(db, tenant_id, schema)

@router.patch("/my-company/settings", response_model=TenantOut)
def update_my_company(
    schema: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_super_admin)
) -> TenantOut:
    """
    Lets a Company Admin update timezone, description, and logo for their own tenant.
    """
    # Force updating only description, logo_url, and timezone. Name, slug, and active status are ignored.
    clean_schema = TenantUpdate(
        description=schema.description,
        logo_url=schema.logo_url,
        timezone=schema.timezone
    )
    return TenantService.update_tenant(db, current_user.tenant_id, clean_schema)

@router.get("/my-company/settings", response_model=TenantOut)
def get_my_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_super_admin)
) -> TenantOut:
    """
    Retrieves the company settings (tenant details) for the authenticated admin.
    """
    return TenantService.get_tenant_details(db, current_user.tenant_id).tenant
