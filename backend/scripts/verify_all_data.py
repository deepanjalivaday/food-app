import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    # Count both tables
    foods_count = conn.execute(text("SELECT COUNT(*) FROM foods")).scalar()
    recipes_count = conn.execute(text("SELECT COUNT(*) FROM recipes")).scalar()
    print(f"✅ Foods (IFCT):    {foods_count} items")
    print(f"✅ Recipes (INDB):  {recipes_count} items")
    print(f"✅ Total:           {foods_count + recipes_count} items")

    # Test search for common Indian foods
    print("\n--- Search tests ---")
    tests = ['rajma', 'rice', 'dal', 'paneer', 'roti', 'chicken', 'spinach']
    
    for query in tests:
        # Check foods table
        r1 = conn.execute(text(
            "SELECT COUNT(*) FROM foods WHERE LOWER(food_name) LIKE :q"
        ), {"q": f"%{query}%"}).scalar()
        
        # Check recipes table
        r2 = conn.execute(text(
            "SELECT COUNT(*) FROM recipes WHERE LOWER(food_name) LIKE :q"
        ), {"q": f"%{query}%"}).scalar()
        
        print(f"  '{query}': {r1} in foods, {r2} in recipes")

    # Show sample from each source
    print("\n--- Sample from foods (IFCT) ---")
    rows = conn.execute(text(
        "SELECT food_name, food_group, energy_kcal, protein_g, is_lab_tested FROM foods LIMIT 5"
    )).fetchall()
    for row in rows:
        print(f"  {row[0]} | {row[1]} | {row[2]} kcal | protein: {row[3]}g | lab tested: {row[4]}")

    print("\n--- Sample from recipes (INDB) ---")
    rows = conn.execute(text(
        "SELECT food_name, energy_kcal, protein_g, is_lab_tested FROM recipes LIMIT 5"
    )).fetchall()
    for row in rows:
        print(f"  {row[0]} | {row[1]} kcal | protein: {row[2]}g | lab tested: {row[3]}")