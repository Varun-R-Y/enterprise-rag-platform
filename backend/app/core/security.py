from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import jwt, JWTError
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from app.core.config import settings

# Initialize password hash using BcryptHasher (as configured in requirements.txt)
password_hash = PasswordHash(hashers=[BcryptHasher()])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    """
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password.
    """
    return password_hash.hash(password)

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a JWT access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[str]:
    """
    Decodes a JWT access token and returns the subject (user ID) if valid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_sub: str | None = payload.get("sub")
        if token_sub is None:
            return None
        return token_sub
    except JWTError:
        return None
