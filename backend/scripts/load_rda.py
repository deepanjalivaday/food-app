import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")
engine = create_engine(os.getenv("DATABASE_URL"))

# ICMR RDA 2024 values
# Source: ICMR-NIN Expert Group, Nutrient Requirements for Indians 2020 (Updated 2024)
# energy_kcal based on activity level (sedentary/moderate/heavy)
# All other values are same regardless of activity level

rda_data = [
    # Children
    {"age_min": 1,  "age_max": 3,  "gender": "both",   "activity_level": "sedentary", "energy_kcal": 1060, "protein_g": 12.5, "calcium_mg": 600,  "iron_mg": 9,  "zinc_mg": 5.0,  "vitc_mg": 40,  "folate_ug": 130, "vita_ug": 400},
    {"age_min": 4,  "age_max": 6,  "gender": "both",   "activity_level": "sedentary", "energy_kcal": 1350, "protein_g": 16.0, "calcium_mg": 600,  "iron_mg": 13, "zinc_mg": 5.5,  "vitc_mg": 40,  "folate_ug": 150, "vita_ug": 400},
    {"age_min": 7,  "age_max": 9,  "gender": "both",   "activity_level": "sedentary", "energy_kcal": 1690, "protein_g": 23.0, "calcium_mg": 600,  "iron_mg": 16, "zinc_mg": 6.5,  "vitc_mg": 40,  "folate_ug": 170, "vita_ug": 600},

    # Boys 10-12
    {"age_min": 10, "age_max": 12, "gender": "male",   "activity_level": "sedentary", "energy_kcal": 2010, "protein_g": 32.0, "calcium_mg": 800,  "iron_mg": 21, "zinc_mg": 8.5,  "vitc_mg": 40,  "folate_ug": 200, "vita_ug": 600},
    # Girls 10-12
    {"age_min": 10, "age_max": 12, "gender": "female", "activity_level": "sedentary", "energy_kcal": 1970, "protein_g": 33.0, "calcium_mg": 800,  "iron_mg": 27, "zinc_mg": 8.5,  "vitc_mg": 40,  "folate_ug": 200, "vita_ug": 600},

    # Boys 13-15
    {"age_min": 13, "age_max": 15, "gender": "male",   "activity_level": "sedentary", "energy_kcal": 2540, "protein_g": 45.0, "calcium_mg": 800,  "iron_mg": 32, "zinc_mg": 14.3, "vitc_mg": 40,  "folate_ug": 200, "vita_ug": 600},
    # Girls 13-15
    {"age_min": 13, "age_max": 15, "gender": "female", "activity_level": "sedentary", "energy_kcal": 2330, "protein_g": 43.0, "calcium_mg": 800,  "iron_mg": 27, "zinc_mg": 12.8, "vitc_mg": 40,  "folate_ug": 200, "vita_ug": 600},

    # Boys 16-18
    {"age_min": 16, "age_max": 18, "gender": "male",   "activity_level": "sedentary", "energy_kcal": 2820, "protein_g": 50.0, "calcium_mg": 800,  "iron_mg": 28, "zinc_mg": 17.6, "vitc_mg": 40,  "folate_ug": 200, "vita_ug": 600},
    # Girls 16-18
    {"age_min": 16, "age_max": 18, "gender": "female", "activity_level": "sedentary", "energy_kcal": 2440, "protein_g": 46.0, "calcium_mg": 800,  "iron_mg": 26, "zinc_mg": 14.2, "vitc_mg": 40,  "folate_ug": 200, "vita_ug": 600},

    # Adult men 19-59 - sedentary
    {"age_min": 19, "age_max": 59, "gender": "male",   "activity_level": "sedentary", "energy_kcal": 2110, "protein_g": 54.0, "calcium_mg": 600,  "iron_mg": 17, "zinc_mg": 17.0, "vitc_mg": 40,  "folate_ug": 220, "vita_ug": 600},
    # Adult men 19-59 - moderate
    {"age_min": 19, "age_max": 59, "gender": "male",   "activity_level": "moderate",  "energy_kcal": 2710, "protein_g": 54.0, "calcium_mg": 600,  "iron_mg": 17, "zinc_mg": 17.0, "vitc_mg": 40,  "folate_ug": 220, "vita_ug": 600},
    # Adult men 19-59 - heavy
    {"age_min": 19, "age_max": 59, "gender": "male",   "activity_level": "heavy",     "energy_kcal": 3490, "protein_g": 54.0, "calcium_mg": 600,  "iron_mg": 17, "zinc_mg": 17.0, "vitc_mg": 40,  "folate_ug": 220, "vita_ug": 600},

    # Adult women 19-59 - sedentary
    {"age_min": 19, "age_max": 59, "gender": "female", "activity_level": "sedentary", "energy_kcal": 1660, "protein_g": 46.0, "calcium_mg": 600,  "iron_mg": 21, "zinc_mg": 13.2, "vitc_mg": 40,  "folate_ug": 220, "vita_ug": 600},
    # Adult women 19-59 - moderate
    {"age_min": 19, "age_max": 59, "gender": "female", "activity_level": "moderate",  "energy_kcal": 2130, "protein_g": 46.0, "calcium_mg": 600,  "iron_mg": 21, "zinc_mg": 13.2, "vitc_mg": 40,  "folate_ug": 220, "vita_ug": 600},
    # Adult women 19-59 - heavy
    {"age_min": 19, "age_max": 59, "gender": "female", "activity_level": "heavy",     "energy_kcal": 2860, "protein_g": 46.0, "calcium_mg": 600,  "iron_mg": 21, "zinc_mg": 13.2, "vitc_mg": 40,  "folate_ug": 220, "vita_ug": 600},

    # Elderly men 60+
    {"age_min": 60, "age_max": 99, "gender": "male",   "activity_level": "sedentary", "energy_kcal": 1900, "protein_g": 54.0, "calcium_mg": 600,  "iron_mg": 17, "zinc_mg": 17.0, "vitc_mg": 40,  "folate_ug": 220, "vita_ug": 600},
    # Elderly women 60+
    {"age_min": 60, "age_max": 99, "gender": "female", "activity_level": "sedentary", "energy_kcal": 1490, "protein_g": 46.0, "calcium_mg": 600,  "iron_mg": 21, "zinc_mg": 13.2, "vitc_mg": 40,  "folate_ug": 220, "vita_ug": 600},

    # Pregnant women
    {"age_min": 19, "age_max": 45, "gender": "pregnant", "activity_level": "sedentary", "energy_kcal": 2060, "protein_g": 55.0, "calcium_mg": 1200, "iron_mg": 35, "zinc_mg": 14.5, "vitc_mg": 60, "folate_ug": 500, "vita_ug": 800},

    # Lactating women
    {"age_min": 19, "age_max": 45, "gender": "lactating", "activity_level": "sedentary", "energy_kcal": 2160, "protein_g": 63.0, "calcium_mg": 1200, "iron_mg": 21, "zinc_mg": 14.1, "vitc_mg": 80, "folate_ug": 350, "vita_ug": 950},
]

print(f"Loading {len(rda_data)} RDA standards...")

inserted = 0
with engine.connect() as conn:
    for row in rda_data:
        conn.execute(text("""
            INSERT INTO nutrient_standards (
                age_min, age_max, gender, activity_level,
                energy_kcal, protein_g, calcium_mg, iron_mg,
                zinc_mg, vitc_mg, folate_ug, vita_ug
            ) VALUES (
                :age_min, :age_max, :gender, :activity_level,
                :energy_kcal, :protein_g, :calcium_mg, :iron_mg,
                :zinc_mg, :vitc_mg, :folate_ug, :vita_ug
            )
        """), row)
        inserted += 1
    conn.commit()

print(f"✅ Loaded {inserted} RDA standards")

# Verify with a test lookup
print("\n--- Test RDA lookup ---")
with engine.connect() as conn:
    # 28 year old sedentary woman
    result = conn.execute(text("""
        SELECT energy_kcal, protein_g, calcium_mg, iron_mg, vitc_mg
        FROM nutrient_standards
        WHERE :age BETWEEN age_min AND age_max
        AND gender = :gender
        AND activity_level = :activity
    """), {"age": 28, "gender": "female", "activity": "sedentary"}).fetchone()

    if result:
        print(f"  28yr sedentary female:")
        print(f"  Energy: {result[0]} kcal | Protein: {result[1]}g | Calcium: {result[2]}mg | Iron: {result[3]}mg | Vit C: {result[4]}mg")

    # 35 year old moderate active man
    result = conn.execute(text("""
        SELECT energy_kcal, protein_g, calcium_mg, iron_mg, vitc_mg
        FROM nutrient_standards
        WHERE :age BETWEEN age_min AND age_max
        AND gender = :gender
        AND activity_level = :activity
    """), {"age": 35, "gender": "male", "activity": "moderate"}).fetchone()

    if result:
        print(f"\n  35yr moderate male:")
        print(f"  Energy: {result[0]} kcal | Protein: {result[1]}g | Calcium: {result[2]}mg | Iron: {result[3]}mg | Vit C: {result[4]}mg")