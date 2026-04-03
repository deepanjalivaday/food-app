import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def hash_password(password: str) -> str:
    """Turn plain text password into a hash"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if plain password matches the hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_token(user_id: int, email: str) -> str:
    """Create a JWT token for a user — no expiry"""
    data = {
        "sub": str(user_id),
        "email": email,
        # 100 years from now = effectively never expires
        "exp": datetime.utcnow() + timedelta(days=36500)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Extract user ID from token — used in protected endpoints"""
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token"
        )
    return int(user_id)