import re
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantOut, TenantDetailsOut
from app.services.tenant_stats_service import TenantStatsService

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text

class TenantService:
    @staticmethod
    def create_tenant(db: Session, schema: TenantCreate) -> Tenant:
        # 1. Determine and slugify the slug
        slug = schema.slug
        if not slug:
            slug = slugify(schema.name)
        else:
            slug = slugify(slug)

        # 2. Check slug uniqueness
        existing = db.query(Tenant).filter(Tenant.slug == slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company slug '{slug}' is already registered."
            )

        # 3. Create Tenant object
        db_tenant = Tenant(
            name=schema.name,
            slug=slug,
            description=schema.description,
            logo_url=schema.logo_url,
            timezone=schema.timezone or "UTC",
            is_active=True
        )
        db.add(db_tenant)
        db.commit()
        db.refresh(db_tenant)
        return db_tenant

    @staticmethod
    def update_tenant(db: Session, tenant_id: uuid.UUID, schema: TenantUpdate) -> Tenant:
        db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not db_tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found."
            )

        # Apply updates
        update_data = schema.model_dump(exclude_unset=True)
        
        # Enforce slug uniqueness if modified
        if "slug" in update_data and update_data["slug"]:
            slug = slugify(update_data["slug"])
            existing = db.query(Tenant).filter(Tenant.slug == slug, Tenant.id != tenant_id).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Company slug '{slug}' is already registered."
                )
            update_data["slug"] = slug

        for key, value in update_data.items():
            setattr(db_tenant, key, value)

        db.commit()
        db.refresh(db_tenant)
        return db_tenant

    @staticmethod
    def list_tenants(db: Session) -> List[Dict[str, Any]]:
        tenants = db.query(Tenant).all()
        results = []
        for t in tenants:
            # Find admin email
            admin_user = db.query(User.email).filter(
                User.tenant_id == t.id,
                User.role == UserRole.ADMIN
            ).first()
            admin_email = admin_user.email if admin_user else None
            
            stats = TenantStatsService.get_stats(db, t.id)
            results.append({
                "tenant": TenantOut.model_validate(t),
                "admin_email": admin_email,
                "stats": stats
            })
        return results

    @staticmethod
    def get_tenant_details(db: Session, tenant_id: uuid.UUID) -> TenantDetailsOut:
        db_tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not db_tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found."
            )
        
        stats = TenantStatsService.get_stats(db, tenant_id)
        return TenantDetailsOut(
            tenant=TenantOut.model_validate(db_tenant),
            stats=stats
        )
