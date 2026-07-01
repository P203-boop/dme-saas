from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "dme-secret-key"
ALGORITHM = "HS256"

# Demo user
fake_user = {
    "username": "admin",
    "password": "admin123"
}


def authenticate_user(username: str, password: str):
    if username == fake_user["username"] and password == fake_user["password"]:
        return fake_user
    return None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
