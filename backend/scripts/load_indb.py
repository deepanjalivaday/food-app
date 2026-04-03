import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")
engine = create_engine(os.getenv("DATABASE_URL"))

# Read the INDB Excel file
print("Reading INDB data...")
df = pd.read_excel("data/raw/Anuvaad_INDB_2024.11.xlsx")
print(f"Found {len(df)} recipes")

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Replace NaN with None
df = df.where(pd.notnull(df), None)

# Map to our recipes table columns
recipes = []
for _, row in df.iterrows():
    recipe = {
        "food_code": row.get("food_code"),
        "food_name": row.get("food_name"),
        "source": "indb2024",
        "is_lab_tested": False,
        "primary_source": row.get("primarysource"),
        "servings_unit": str(row.get("servings_unit")) if row.get("servings_unit") else None,
        "energy_kj": row.get("energy_kj"),
        "energy_kcal": row.get("energy_kcal"),
        "carb_g": row.get("carb_g"),
        "protein_g": row.get("protein_g"),
        "fat_g": row.get("fat_g"),
        "freesugar_g": row.get("freesugar_g"),
        "fibre_g": row.get("fibre_g"),
        "sfa_mg": row.get("sfa_mg"),
        "mufa_mg": row.get("mufa_mg"),
        "pufa_mg": row.get("pufa_mg"),
        "cholesterol_mg": row.get("cholesterol_mg"),
        "calcium_mg": row.get("calcium_mg"),
        "phosphorus_mg": row.get("phosphorus_mg"),
        "magnesium_mg": row.get("magnesium_mg"),
        "sodium_mg": row.get("sodium_mg"),
        "potassium_mg": row.get("potassium_mg"),
        "iron_mg": row.get("iron_mg"),
        "copper_mg": row.get("copper_mg"),
        "selenium_ug": row.get("selenium_ug"),
        "zinc_mg": row.get("zinc_mg"),
        "vita_ug": row.get("vita_ug"),
        "vite_mg": row.get("vite_mg"),
        "vitd2_ug": row.get("vitd2_ug"),
        "vitd3_ug": row.get("vitd3_ug"),
        "vitk1_ug": row.get("vitk1_ug"),
        "folate_ug": row.get("folate_ug"),
        "vitb1_mg": row.get("vitb1_mg"),
        "vitb2_mg": row.get("vitb2_mg"),
        "vitb3_mg": row.get("vitb3_mg"),
        "vitb6_mg": row.get("vitb6_mg"),
        "vitc_mg": row.get("vitc_mg"),
        "carotenoids_ug": row.get("carotenoids_ug"),
        "unit_serving_energy_kcal": row.get("unit_serving_energy_kcal"),
        "unit_serving_carb_g": row.get("unit_serving_carb_g"),
        "unit_serving_protein_g": row.get("unit_serving_protein_g"),
        "unit_serving_fat_g": row.get("unit_serving_fat_g"),
        "unit_serving_fibre_g": row.get("unit_serving_fibre_g"),
        "unit_serving_calcium_mg": row.get("unit_serving_calcium_mg"),
        "unit_serving_iron_mg": row.get("unit_serving_iron_mg"),
        "unit_serving_vitc_mg": row.get("unit_serving_vitc_mg"),
    }
    recipes.append(recipe)

# Insert into database
print("Loading into database...")
with engine.connect() as conn:
    conn.execute(
        __import__('sqlalchemy').text("""
            INSERT INTO recipes (
                food_code, food_name, source, is_lab_tested, primary_source, servings_unit,
                energy_kj, energy_kcal, carb_g, protein_g, fat_g, freesugar_g, fibre_g,
                sfa_mg, mufa_mg, pufa_mg, cholesterol_mg, calcium_mg, phosphorus_mg,
                magnesium_mg, sodium_mg, potassium_mg, iron_mg, copper_mg, selenium_ug,
                zinc_mg, vita_ug, vite_mg, vitd2_ug, vitd3_ug, vitk1_ug, folate_ug,
                vitb1_mg, vitb2_mg, vitb3_mg, vitb6_mg, vitc_mg, carotenoids_ug,
                unit_serving_energy_kcal, unit_serving_carb_g, unit_serving_protein_g,
                unit_serving_fat_g, unit_serving_fibre_g, unit_serving_calcium_mg,
                unit_serving_iron_mg, unit_serving_vitc_mg
            ) VALUES (
                :food_code, :food_name, :source, :is_lab_tested, :primary_source, :servings_unit,
                :energy_kj, :energy_kcal, :carb_g, :protein_g, :fat_g, :freesugar_g, :fibre_g,
                :sfa_mg, :mufa_mg, :pufa_mg, :cholesterol_mg, :calcium_mg, :phosphorus_mg,
                :magnesium_mg, :sodium_mg, :potassium_mg, :iron_mg, :copper_mg, :selenium_ug,
                :zinc_mg, :vita_ug, :vite_mg, :vitd2_ug, :vitd3_ug, :vitk1_ug, :folate_ug,
                :vitb1_mg, :vitb2_mg, :vitb3_mg, :vitb6_mg, :vitc_mg, :carotenoids_ug,
                :unit_serving_energy_kcal, :unit_serving_carb_g, :unit_serving_protein_g,
                :unit_serving_fat_g, :unit_serving_fibre_g, :unit_serving_calcium_mg,
                :unit_serving_iron_mg, :unit_serving_vitc_mg
            )
        """),
        recipes
    )
    conn.commit()

print(f"✅ Successfully loaded {len(recipes)} recipes into database")