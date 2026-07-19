import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, CompanyAdminCreate
from app.core.security import get_password_hash

def create_employee(db: Session, schema: UserCreate, tenant_id: uuid.UUID, admin_id: uuid.UUID) -> User:
    """
    Creates an employee account associated with the admin's tenant.
    Assigns role = EMPLOYEE and created_by = admin_id.
    Prevents duplicate emails.
    """
    # 1. Prevent duplicate email registration
    existing_user = db.query(User).filter(User.email == schema.email).first()
    if existing_user:
        raise ValueError("A user with this email address already exists.")

    # 2. Hash password and save new employee
    hashed_pwd = get_password_hash(schema.password)
    user = User(
        email=schema.email,
        hashed_password=hashed_pwd,
        full_name=schema.full_name,
        tenant_id=tenant_id,
        role=UserRole.EMPLOYEE,
        created_by=admin_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_company_admin(db: Session, schema: CompanyAdminCreate, creator_id: uuid.UUID) -> User:
    """
    Creates a Company Admin account associated with the specified tenant.
    Assigns role = ADMIN and created_by = creator_id.
    Prevents duplicate emails.
    """
    # 1. Prevent duplicate email registration
    existing_user = db.query(User).filter(User.email == schema.email).first()
    if existing_user:
        raise ValueError("A user with this email address already exists.")

    # 2. Hash password and save new admin
    hashed_pwd = get_password_hash(schema.password)
    user = User(
        email=schema.email,
        hashed_password=hashed_pwd,
        full_name=schema.full_name,
        tenant_id=schema.tenant_id,
        role=UserRole.ADMIN,
        created_by=creator_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def list_tenant_users(db: Session, tenant_id: uuid.UUID) -> List[User]:
    """
    Returns only users belonging to the specified tenant.
    """
    return db.query(User).filter(User.tenant_id == tenant_id).all()

def list_all_users(db: Session) -> List[User]:
    """
    Returns all users across all tenants.
    """
    return db.query(User).all()

def delete_tenant_user(db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID, current_user_id: uuid.UUID, is_super_admin: bool = False) -> None:
    """
    Deletes a user belonging to the tenant.
    Prevents self-deletion.
    """
    if user_id == current_user_id:
        raise ValueError("Users cannot delete themselves.")

    if is_super_admin:
        user = db.query(User).filter(User.id == user_id).first()
    else:
        user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()

    if not user:
        raise ValueError("User not found.")

    db.delete(user)
    db.commit()
