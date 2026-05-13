# backend/schemas/auth_security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from database import async_session
from sqlalchemy import select
from models import Employee, Reader
from schemas.schemas import TokenData

SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_change_in_production_12345")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

ROLE_PERMISSIONS = {
    "admin": ["users:manage", "settings:edit", "audit:view", "genres:manage", "reports:view", "books:read", "books:write", "loans:manage", "reservations:manage"],
    "librarian": ["books:read", "books:write", "loans:manage", "reservations:manage", "reports:view"],
    "reader": ["loans:view", "reservations:manage", "profile:edit"]
}

def require_admin_or_librarian(user):
    if not hasattr(user, 'role') or user.role not in ["admin", "librarian"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return user

def require_admin(user):
    if not hasattr(user, 'role') or user.role != "admin":
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = TokenData(login=login)
    except JWTError:
        raise credentials_exception

    user = None
    async with async_session() as session:
        result = await session.execute(select(Employee).where(Employee.login == token_data.login))
        user = result.scalar_one_or_none()
        if not user:
            result = await session.execute(select(Reader).where(Reader.login == token_data.login))
            user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception
    return user