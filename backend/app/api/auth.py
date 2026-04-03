from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from app.db.database import get_db
from app.services.auth_utils import (
    hash_password, verify_password,
    create_token, get_current_user_id
)

router = APIRouter()

# --- Request/Response models ---

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    activity_level: str = "sedentary"
    dietary_preference: str = "vegetarian"

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Endpoints ---

@router.post("/auth/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""

    # Check if email already exists
    existing = db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": request.email}
    ).fetchone()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Validate gender
    if request.gender not in ["male", "female"]:
        raise HTTPException(
            status_code=400,
            detail="gender must be 'male' or 'female'"
        )

    # Validate activity level
    if request.activity_level not in ["sedentary", "moderate", "heavy"]:
        raise HTTPException(
            status_code=400,
            detail="activity_level must be 'sedentary', 'moderate', or 'heavy'"
        )

    # Hash password
    password_hash = hash_password(request.password)

    # Insert user
    result = db.execute(text("""
        INSERT INTO users (
            email, name, password_hash, age, gender,
            weight_kg, height_cm, activity_level, dietary_preference
        ) VALUES (
            :email, :name, :password_hash, :age, :gender,
            :weight_kg, :height_cm, :activity_level, :dietary_preference
        )
        RETURNING id
    """), {
        "email": request.email,
        "name": request.name,
        "password_hash": password_hash,
        "age": request.age,
        "gender": request.gender,
        "weight_kg": request.weight_kg,
        "height_cm": request.height_cm,
        "activity_level": request.activity_level,
        "dietary_preference": request.dietary_preference
    })
    db.commit()

    user_id = result.fetchone()[0]
    token = create_token(user_id, request.email)

    return {
        "message": "Registration successful",
        "token": token,
        "user": {
            "id": user_id,
            "name": request.name,
            "email": request.email,
            "age": request.age,
            "gender": request.gender,
            "activity_level": request.activity_level,
            "dietary_preference": request.dietary_preference
        }
    }


@router.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""

    # Find user
    user = db.execute(
        text("SELECT id, email, name, password_hash, age, gender, activity_level, dietary_preference FROM users WHERE email = :email"),
        {"email": request.email}
    ).fetchone()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check password
    if not verify_password(request.password, user[3]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_token(user[0], user[1])

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user[0],
            "email": user[1],
            "name": user[2],
            "age": user[4],
            "gender": user[5],
            "activity_level": user[6],
            "dietary_preference": user[7]
        }
    }


@router.get("/auth/me")
def get_me(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current logged in user's profile"""

    user = db.execute(
        text("SELECT id, email, name, age, gender, weight_kg, height_cm, activity_level, dietary_preference FROM users WHERE id = :id"),
        {"id": user_id}
    ).fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user[0],
        "email": user[1],
        "name": user[2],
        "age": user[3],
        "gender": user[4],
        "weight_kg": user[5],
        "height_cm": user[6],
        "activity_level": user[7],
        "dietary_preference": user[8]
    }