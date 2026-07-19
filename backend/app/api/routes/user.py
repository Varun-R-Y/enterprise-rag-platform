import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import require_admin, require_super_admin, require_admin_or_super_admin
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut, CompanyAdminCreate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create an employee user",
    description="Allows administrators to create employee accounts for their tenant. Client parameters for role or tenant_id are ignored."
)
def create_tenant_employee(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> UserOut:
    """
    Endpoint to create employee users under the admin's tenant.
    """
    try:
        user = user_service.create_employee(
            db=db,
            schema=payload,
            tenant_id=current_admin.tenant_id,
            admin_id=current_admin.id
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/company-admin",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a company admin user",
    description="Allows super admins to create company admin accounts for any tenant."
)
def create_company_admin_user(
    payload: CompanyAdminCreate,
    db: Session = Depends(get_db),
    current_super_admin: User = Depends(require_super_admin)
) -> UserOut:
    """
    Endpoint for Super Admins to create Company Admins for a specific tenant.
    """
    try:
        user = user_service.create_company_admin(
            db=db,
            schema=payload,
            creator_id=current_super_admin.id
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "",
    response_model=list[UserOut],
    summary="List users",
    description="Returns all users in the system if Super Admin, or tenant users if Company Admin."
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_super_admin)
) -> list[UserOut]:
    """
    Endpoint to list users depending on the requester's role.
    """
    if current_user.role == UserRole.SUPER_ADMIN:
        return user_service.list_all_users(db=db)
    return user_service.list_tenant_users(db=db, tenant_id=current_user.tenant_id)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Deletes a user. Super Admins can delete any user; Company Admins can delete users under their tenant only."
)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_super_admin)
) -> None:
    """
    Endpoint to delete a user account.
    """
    try:
        is_super = current_user.role == UserRole.SUPER_ADMIN
        user_service.delete_tenant_user(
            db=db,
            tenant_id=current_user.tenant_id,
            user_id=user_id,
            current_user_id=current_user.id,
            is_super_admin=is_super
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
