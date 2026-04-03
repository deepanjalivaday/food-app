import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")
engine = create_engine(os.getenv("DATABASE_URL"))

print("Reading IFCT 2017 data...")
with open(r"C:\Users\Avadh\Desktop\musu\food-app\backend\data\raw\ifct2017.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"Found {len(raw_data)} items")

# Keys are now clean like 'Food Code; code' - extract short code after semicolon
def get_val(item, short_code):
    for k, v in item.items():
        if ';' in k:
            after_semi = k.split(';')[1].strip()
            if after_semi == short_code:
                if v is None or v == '' or v == 'None':
                    return None
                return v
    return None

def to_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except:
        return None

# Verify extraction on first item
item = raw_data[0]
print("\nVerification on first item:")
print(f"  code:     {get_val(item, 'code')}")
print(f"  name:     {get_val(item, 'name')}")
print(f"  grup:     {get_val(item, 'grup')}")
print(f"  enerc:    {get_val(item, 'enerc')} kJ")
print(f"  protcnt:  {get_val(item, 'protcnt')} g")
print(f"  fatce:    {get_val(item, 'fatce')} g")
print(f"  choavldf: {get_val(item, 'choavldf')} g")
print(f"  ca:       {get_val(item, 'ca')} g/100g")
print(f"  fe:       {get_val(item, 'fe')} g/100g")

# Build foods list
print("\nBuilding foods list...")
foods = []
for item in raw_data:
    enerc   = to_float(get_val(item, 'enerc'))
    ca      = to_float(get_val(item, 'ca'))
    fe      = to_float(get_val(item, 'fe'))
    na      = to_float(get_val(item, 'na'))
    k       = to_float(get_val(item, 'k'))
    zn      = to_float(get_val(item, 'zn'))
    vitc    = to_float(get_val(item, 'vitc'))
    vita    = to_float(get_val(item, 'vita'))
    folsum  = to_float(get_val(item, 'folsum'))

    food = {
        "food_code":    get_val(item, 'code'),
        "food_name":    get_val(item, 'name'),
        "source":       "ifct2017",
        "is_lab_tested": True,
        "food_group":   get_val(item, 'grup'),
        # Energy: kJ → kcal
        "energy_kcal":  round(enerc / 4.184, 2) if enerc else None,
        "carb_g":       to_float(get_val(item, 'choavldf')),
        "protein_g":    to_float(get_val(item, 'protcnt')),
        "fat_g":        to_float(get_val(item, 'fatce')),
        "fibre_g":      to_float(get_val(item, 'fibtg')),
        # Minerals: g/100g → mg (*1000)
        "calcium_mg":   round(ca * 1000, 3) if ca else None,
        "iron_mg":      round(fe * 1000, 3) if fe else None,
        "sodium_mg":    round(na * 1000, 3) if na else None,
        "potassium_mg": round(k  * 1000, 3) if k  else None,
        "zinc_mg":      round(zn * 1000, 3) if zn else None,
        # Vitamins: g/100g → mg (*1000) or ug (*1000000)
        "vitc_mg":      round(vitc   * 1000,    3) if vitc   else None,
        "vita_ug":      round(vita   * 1000000, 3) if vita   else None,
        "folate_ug":    round(folsum * 1000000, 3) if folsum else None,
    }
    foods.append(food)

print(f"Built {len(foods)} items")
print(f"Sample: {foods[0]['food_name']} | {foods[0]['energy_kcal']} kcal | protein: {foods[0]['protein_g']}g | calcium: {foods[0]['calcium_mg']}mg")

# Insert - each in own transaction
print("\nInserting into database...")
inserted = 0
skipped  = 0

for food in foods:
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO foods (
                    food_code, food_name, source, is_lab_tested, food_group,
                    energy_kcal, carb_g, protein_g, fat_g, fibre_g,
                    calcium_mg, iron_mg, sodium_mg, potassium_mg, zinc_mg,
                    vitc_mg, vita_ug, folate_ug
                ) VALUES (
                    :food_code, :food_name, :source, :is_lab_tested, :food_group,
                    :energy_kcal, :carb_g, :protein_g, :fat_g, :fibre_g,
                    :calcium_mg, :iron_mg, :sodium_mg, :potassium_mg, :zinc_mg,
                    :vitc_mg, :vita_ug, :folate_ug
                )
                ON CONFLICT (food_code) DO NOTHING
            """), food)
            conn.commit()
            inserted += 1
    except Exception as e:
        skipped += 1
        print(f"  Skipped {food.get('food_code')} - {food.get('food_name')}: {str(e)[:100]}")

print(f"\n✅ Inserted: {inserted} | Skipped: {skipped}")