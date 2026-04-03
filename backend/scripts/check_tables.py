import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
    print("Tables in database:")
    for row in result:
        print(f"  ✅ {row[0]}")