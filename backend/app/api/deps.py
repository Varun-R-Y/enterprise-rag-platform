import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import decode_token
from app.models.user import User

# Configuration for OAuth2 password flow pointing to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to retrieve the currently authenticated user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Decode token to extract subject (user ID)
    user_id_str = decode_token(token)
    if not user_id_str:
        raise credentials_exception
        
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception
        
    # 2. Look up the user in the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user."
        )
        
    return user


from app.models.user import UserRole
from app.models.tenant import Tenant

def verify_tenant_active(db: Session, tenant_id: uuid.UUID) -> None:
    """
    Verifies that the tenant exists and is active.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is deactivated."
        )

def require_active_tenant_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifies that the user belongs to an active tenant (except for Super Admins).
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        verify_tenant_active(db, current_user.tenant_id)
    return current_user

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to verify that the current user has the SUPER_ADMIN role.
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin privileges required."
        )
    return current_user

def require_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to verify that the current user has the ADMIN role and belongs to an active tenant.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required."
        )
    verify_tenant_active(db, current_user.tenant_id)
    return current_user

def require_employee(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to verify that the current user has the EMPLOYEE role and belongs to an active tenant.
    """
    if current_user.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee privileges required."
        )
    verify_tenant_active(db, current_user.tenant_id)
    return current_user

def require_admin_or_super_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to verify that the current user has either the ADMIN or SUPER_ADMIN role.
    Verifies active tenant only for the ADMIN role.
    """
    if current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Super Admin privileges required."
        )
    if current_user.role == UserRole.ADMIN:
        verify_tenant_active(db, current_user.tenant_id)
    return current_user
