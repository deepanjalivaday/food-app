from sqlalchemy import Column, Integer, String, Float, ARRAY
from sqlalchemy.sql.sqltypes import Boolean
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    password_hash = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    weight_kg = Column(Float)
    height_cm = Column(Float)
    activity_level = Column(String, default="sedentary")
    dietary_preference = Column(String, default="vegetarian")