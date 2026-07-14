from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import UserRegister, UserOut, Token
from app.services.auth import register_user, authenticate_user
from app.core.security import create_access_token
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    schema: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Registers a new user under an existing tenant.
    """
    return register_user(db=db, schema=schema)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, returning a JWT access token.
    Matches username (email) and password from form data.
    """
    user = authenticate_user(db=db, email=form_data.username, password=form_data.password)
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserOut)
def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the currently authenticated user's profile.
    """
    return current_user
