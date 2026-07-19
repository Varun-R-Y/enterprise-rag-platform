import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")

class CompanyAdminCreate(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8, description="Admin password (min 8 characters)")
    tenant_id: uuid.UUID

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    tenant_id: uuid.UUID
    is_active: bool
    created_by: Optional[uuid.UUID] = None

    @field_validator("role", mode="before")
    @classmethod
    def capitalize_role(cls, v):
        if isinstance(v, str):
            return v.upper()
        if hasattr(v, "value"):
            return v.value.upper()
        return v

    model_config = {
        "from_attributes": True
    }
