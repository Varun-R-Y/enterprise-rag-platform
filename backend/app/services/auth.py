from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.schemas.auth import UserRegister
from app.core.security import get_password_hash, verify_password

def register_user(db: Session, schema: UserRegister) -> User:
    """
    Registers a new user under an existing tenant.
    
    Verifies that the tenant exists and that the email is unique before
    hashing the password and creating the database record.
    """
    # 1. Verify tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == schema.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified tenant does not exist."
        )
    
    # 2. Verify email uniqueness
    existing_user = db.query(User).filter(User.email == schema.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    # 3. Hash password and save new user
    hashed_pwd = get_password_hash(schema.password)
    user = User(
        email=schema.email,
        hashed_password=hashed_pwd,
        full_name=schema.full_name,
        tenant_id=schema.tenant_id,
        role=UserRole.EMPLOYEE,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Validates user credentials against stored hashes.
    
    Returns the user object if authenticated, otherwise raises an unauthorized exception.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive."
        )
        
    return user
