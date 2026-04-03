import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Give it the exact path to your .env file
load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")