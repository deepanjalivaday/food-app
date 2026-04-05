from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import search, auth, meals

app = FastAPI(
    title="Food Nutrition API",
    description="Indian food nutrition tracker API",
    version="1.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(auth.router,   prefix="/api/v1", tags=["auth"])
app.include_router(meals.router,  prefix="/api/v1", tags=["meals"])

@app.get("/")
def root():
    return {"message": "Food Nutrition API is running"}