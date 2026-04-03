import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Read the schema file
with open("app/db/schema.sql", "r") as f:
    schema = f.read()

# Execute it
with engine.connect() as conn:
    # Split by semicolon and run each statement
    statements = [s.strip() for s in schema.split(";") if s.strip()]
    for statement in statements:
        conn.execute(text(statement))
    conn.commit()
    print("✅ All tables created successfully")