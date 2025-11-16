from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer  # <-- IMPORTANTE
from core.config import settings

# OAuth2PasswordBearer para extracción de token desde "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

MAX_PASSWORD_LEN = 256

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_password_hash(password: str) -> str:
    if len(password) > MAX_PASSWORD_LEN:
        password = password[:MAX_PASSWORD_LEN]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password) > MAX_PASSWORD_LEN:
        plain_password = plain_password[:MAX_PASSWORD_LEN]
    return pwd_context.verify(plain_password, hashed_password)
