import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")
engine = create_engine(os.getenv("DATABASE_URL"))

print("Reading INDB data...")
df = pd.read_excel(r"C:\Users\Avadh\Desktop\musu\food-app\backend\data\raw\Anuvaad_INDB_2024.11.xlsx")
print(f"Found {len(df)} recipes")

df.columns = df.columns.str.strip().str.lower()

def clean(val):
    if val is None:
        return None
    if isinstance(val, float) and np.isnan(val):
        return None
    return val

recipes = []
for _, row in df.iterrows():
    recipe = {
        "food_code": clean(row.get("food_code")),
        "food_name": clean(row.get("food_name")),
        "source": "indb2024",
        "is_lab_tested": False,
        "primary_source": clean(row.get("primarysource")),
        "servings_unit": str(row.get("servings_unit")) if row.get("servings_unit") and not (isinstance(row.get("servings_unit"), float) and np.isnan(row.get("servings_unit"))) else None,
        "energy_kj": clean(row.get("energy_kj")),
        "energy_kcal": clean(row.get("energy_kcal")),
        "carb_g": clean(row.get("carb_g")),
        "protein_g": clean(row.get("protein_g")),
        "fat_g": clean(row.get("fat_g")),
        "freesugar_g": clean(row.get("freesugar_g")),
        "fibre_g": clean(row.get("fibre_g")),
        "sfa_mg": clean(row.get("sfa_mg")),
        "mufa_mg": clean(row.get("mufa_mg")),
        "pufa_mg": clean(row.get("pufa_mg")),
        "cholesterol_mg": clean(row.get("cholesterol_mg")),
        "calcium_mg": clean(row.get("calcium_mg")),
        "phosphorus_mg": clean(row.get("phosphorus_mg")),
        "magnesium_mg": clean(row.get("magnesium_mg")),
        "sodium_mg": clean(row.get("sodium_mg")),
        "potassium_mg": clean(row.get("potassium_mg")),
        "iron_mg": clean(row.get("iron_mg")),
        "copper_mg": clean(row.get("copper_mg")),
        "selenium_ug": clean(row.get("selenium_ug")),
        "zinc_mg": clean(row.get("zinc_mg")),
        "vita_ug": clean(row.get("vita_ug")),
        "vite_mg": clean(row.get("vite_mg")),
        "vitd2_ug": clean(row.get("vitd2_ug")),
        "vitd3_ug": clean(row.get("vitd3_ug")),
        "vitk1_ug": clean(row.get("vitk1_ug")),
        "folate_ug": clean(row.get("folate_ug")),
        "vitb1_mg": clean(row.get("vitb1_mg")),
        "vitb2_mg": clean(row.get("vitb2_mg")),
        "vitb3_mg": clean(row.get("vitb3_mg")),
        "vitb6_mg": clean(row.get("vitb6_mg")),
        "vitc_mg": clean(row.get("vitc_mg")),
        "carotenoids_ug": clean(row.get("carotenoids_ug")),
        "unit_serving_energy_kcal": clean(row.get("unit_serving_energy_kcal")),
        "unit_serving_carb_g": clean(row.get("unit_serving_carb_g")),
        "unit_serving_protein_g": clean(row.get("unit_serving_protein_g")),
        "unit_serving_fat_g": clean(row.get("unit_serving_fat_g")),
        "unit_serving_fibre_g": clean(row.get("unit_serving_fibre_g")),
        "unit_serving_calcium_mg": clean(row.get("unit_serving_calcium_mg")),
        "unit_serving_iron_mg": clean(row.get("unit_serving_iron_mg")),
        "unit_serving_vitc_mg": clean(row.get("unit_serving_vitc_mg")),
    }
    recipes.append(recipe)

print("Loading into database one by one...")
inserted = 0
skipped = 0

for recipe in recipes:
    try:
        with engine.connect() as conn:
            conn.execute(text("""
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
                ON CONFLICT (food_code) DO NOTHING
            """), recipe)
            conn.commit()
            inserted += 1
    except Exception as e:
        skipped += 1
        print(f"Skipped {recipe.get('food_code')} - {recipe.get('food_name')}: {str(e)[:150]}")

print(f"\n✅ Inserted: {inserted} | Skipped: {skipped}")