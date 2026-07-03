import hmac
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
ADMIN_USERNAME = os.getenv("DME_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("DME_ADMIN_PASSWORD", "admin123")
ADMIN_PASSWORD_HASH = os.getenv("DME_ADMIN_PASSWORD_HASH")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    username_matches = hmac.compare_digest(username, ADMIN_USERNAME)
    if not username_matches:
        return None

    if ADMIN_PASSWORD_HASH:
        password_matches = verify_password(password, ADMIN_PASSWORD_HASH)
    else:
        password_matches = hmac.compare_digest(password, ADMIN_PASSWORD)

    if not password_matches:
        return None

    return {"username": ADMIN_USERNAME}


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError as exc:
        raise credentials_error from exc

    if not username or not hmac.compare_digest(username, ADMIN_USERNAME):
        raise credentials_error

    return {"username": username}
