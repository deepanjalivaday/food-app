import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    # Total count
    count = conn.execute(text("SELECT COUNT(*) FROM recipes")).scalar()
    print(f"✅ Total recipes: {count}")

    # Sample 5 recipes
    print("\nSample recipes:")
    result = conn.execute(text("SELECT food_code, food_name, energy_kcal, protein_g, carb_g, fat_g FROM recipes LIMIT 5"))
    for row in result:
        print(f"  {row[0]} | {row[1]} | {row[2]} kcal | protein: {row[3]}g | carbs: {row[4]}g | fat: {row[5]}g")

    # Search test - try finding rajma
    print("\nSearch test for 'rajma':")
    result = conn.execute(text("SELECT food_code, food_name, energy_kcal FROM recipes WHERE LOWER(food_name) LIKE '%rajma%'"))
    rows = result.fetchall()
    if rows:
        for row in rows:
            print(f"  ✅ Found: {row[0]} | {row[1]} | {row[2]} kcal")
    else:
        print("  ❌ Not found")

    # Search test - try finding dal
    print("\nSearch test for 'dal':")
    result = conn.execute(text("SELECT food_code, food_name, energy_kcal FROM recipes WHERE LOWER(food_name) LIKE '%dal%' LIMIT 5"))
    rows = result.fetchall()
    if rows:
        for row in rows:
            print(f"  ✅ Found: {row[0]} | {row[1]} | {row[2]} kcal")
    else:
        print("  ❌ Not found")