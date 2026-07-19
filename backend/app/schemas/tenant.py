import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1)
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: Optional[str] = "UTC"

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None

class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class TenantStats(BaseModel):
    employees_count: int
    admins_count: int
    documents_count: int
    chunks_count: int
    conversations_count: int
    storage_used_bytes: int

class TenantDetailsOut(BaseModel):
    tenant: TenantOut
    stats: TenantStats

class TenantListResponse(BaseModel):
    tenant: TenantOut
    admin_email: Optional[str] = None
    stats: TenantStats
