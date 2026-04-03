from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from app.db.database import get_db
from app.services.auth_utils import get_current_user_id
from datetime import date
from typing import Optional

router = APIRouter()

# --- Request models ---

class MealLogRequest(BaseModel):
    food_id: int
    food_type: str        # 'ingredient' or 'recipe'
    quantity_g: float
    meal_type: str        # 'breakfast', 'lunch', 'dinner', 'snack'

# --- Endpoints ---

@router.post("/meals/log")
def log_meal(
    request: MealLogRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Log a meal for the current user"""

    # Validate meal type
    if request.meal_type not in ["breakfast", "lunch", "dinner", "snack"]:
        raise HTTPException(
            status_code=400,
            detail="meal_type must be 'breakfast', 'lunch', 'dinner', or 'snack'"
        )

    # Validate food type
    if request.food_type not in ["ingredient", "recipe"]:
        raise HTTPException(
            status_code=400,
            detail="food_type must be 'ingredient' or 'recipe'"
        )

    # Look up the food
    if request.food_type == "ingredient":
        food = db.execute(text("""
            SELECT food_name, energy_kcal, protein_g, carb_g, fat_g,
                   fibre_g, calcium_mg, iron_mg, vitc_mg
            FROM foods WHERE id = :id
        """), {"id": request.food_id}).fetchone()
    else:
        food = db.execute(text("""
            SELECT food_name, energy_kcal, protein_g, carb_g, fat_g,
                   fibre_g, calcium_mg, iron_mg, vitc_mg
            FROM recipes WHERE id = :id
        """), {"id": request.food_id}).fetchone()

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    # Calculate nutrients based on quantity
    # All values in DB are per 100g, so multiply by (quantity/100)
    multiplier = request.quantity_g / 100

    def calc(val):
        return round(val * multiplier, 2) if val else None

    # Save meal log
    db.execute(text("""
        INSERT INTO meal_logs (
            user_id, food_id, food_type, food_name, quantity_g, meal_type,
            energy_kcal, protein_g, carb_g, fat_g, fibre_g,
            calcium_mg, iron_mg, vitc_mg
        ) VALUES (
            :user_id, :food_id, :food_type, :food_name, :quantity_g, :meal_type,
            :energy_kcal, :protein_g, :carb_g, :fat_g, :fibre_g,
            :calcium_mg, :iron_mg, :vitc_mg
        )
    """), {
        "user_id": user_id,
        "food_id": request.food_id,
        "food_type": request.food_type,
        "food_name": food[0],
        "quantity_g": request.quantity_g,
        "meal_type": request.meal_type,
        "energy_kcal": calc(food[1]),
        "protein_g": calc(food[2]),
        "carb_g": calc(food[3]),
        "fat_g": calc(food[4]),
        "fibre_g": calc(food[5]),
        "calcium_mg": calc(food[6]),
        "iron_mg": calc(food[7]),
        "vitc_mg": calc(food[8])
    })
    db.commit()

    return {
        "message": "Meal logged successfully",
        "meal": {
            "food_name": food[0],
            "quantity_g": request.quantity_g,
            "meal_type": request.meal_type,
            "nutrients": {
                "energy_kcal": calc(food[1]),
                "protein_g": calc(food[2]),
                "carb_g": calc(food[3]),
                "fat_g": calc(food[4]),
                "fibre_g": calc(food[5]),
                "calcium_mg": calc(food[6]),
                "iron_mg": calc(food[7]),
                "vitc_mg": calc(food[8])
            }
        }
    }


@router.get("/meals/today")
def get_today_meals(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all meals logged today with nutrient totals"""

    # Get today's meals
    meals = db.execute(text("""
        SELECT food_name, quantity_g, meal_type,
               energy_kcal, protein_g, carb_g, fat_g,
               fibre_g, calcium_mg, iron_mg, vitc_mg,
               logged_at
        FROM meal_logs
        WHERE user_id = :user_id
        AND DATE(logged_at) = CURRENT_DATE
        ORDER BY logged_at
    """), {"user_id": user_id}).fetchall()

    # Build meal list
    meal_list = []
    for m in meals:
        meal_list.append({
            "food_name": m[0],
            "quantity_g": m[1],
            "meal_type": m[2],
            "energy_kcal": m[3],
            "protein_g": m[4],
            "carb_g": m[5],
            "fat_g": m[6],
            "fibre_g": m[7],
            "calcium_mg": m[8],
            "iron_mg": m[9],
            "vitc_mg": m[10],
            "logged_at": str(m[11])
        })

    # Calculate totals
    def total(index):
        vals = [m[index] for m in meals if m[index]]
        return round(sum(vals), 2) if vals else 0

    totals = {
        "energy_kcal": total(3),
        "protein_g": total(4),
        "carb_g": total(5),
        "fat_g": total(6),
        "fibre_g": total(7),
        "calcium_mg": total(8),
        "iron_mg": total(9),
        "vitc_mg": total(10)
    }

    # Get user's RDA targets
    user = db.execute(text("""
        SELECT age, gender, activity_level FROM users WHERE id = :id
    """), {"id": user_id}).fetchone()

    rda = db.execute(text("""
        SELECT energy_kcal, protein_g, calcium_mg, iron_mg, vitc_mg
        FROM nutrient_standards
        WHERE :age BETWEEN age_min AND age_max
        AND gender = :gender
        AND activity_level = :activity
    """), {
        "age": user[0],
        "gender": user[1],
        "activity": user[2]
    }).fetchone()

    # Calculate percentage of RDA met
    rda_comparison = {}
    if rda:
        nutrients = ["energy_kcal", "protein_g", "calcium_mg", "iron_mg", "vitc_mg"]
        rda_vals = [rda[0], rda[1], rda[2], rda[3], rda[4]]
        total_vals = [totals["energy_kcal"], totals["protein_g"],
                     totals["calcium_mg"], totals["iron_mg"], totals["vitc_mg"]]

        for nutrient, rda_val, actual in zip(nutrients, rda_vals, total_vals):
            pct = round((actual / rda_val) * 100, 1) if rda_val else None
            rda_comparison[nutrient] = {
                "consumed": actual,
                "target": rda_val,
                "percentage": pct,
                "status": "good" if pct and pct >= 80 else "low"
            }

    return {
        "date": str(date.today()),
        "meals": meal_list,
        "totals": totals,
        "rda_comparison": rda_comparison
    }
@router.get("/meals/recommendations")
def get_recommendations(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get food recommendations based on today's nutrient gaps"""

    # Get user profile
    user = db.execute(text("""
        SELECT age, gender, activity_level, dietary_preference 
        FROM users WHERE id = :id
    """), {"id": user_id}).fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    age, gender, activity_level, dietary_preference = user

    # Get today's nutrient totals
    totals = db.execute(text("""
        SELECT 
            COALESCE(SUM(energy_kcal), 0),
            COALESCE(SUM(protein_g), 0),
            COALESCE(SUM(calcium_mg), 0),
            COALESCE(SUM(iron_mg), 0),
            COALESCE(SUM(vitc_mg), 0),
            COALESCE(SUM(fibre_g), 0)
        FROM meal_logs
        WHERE user_id = :user_id
        AND DATE(logged_at) = CURRENT_DATE
    """), {"user_id": user_id}).fetchone()

    # Get RDA targets
    rda = db.execute(text("""
        SELECT energy_kcal, protein_g, calcium_mg, iron_mg, vitc_mg
        FROM nutrient_standards
        WHERE :age BETWEEN age_min AND age_max
        AND gender = :gender
        AND activity_level = :activity
    """), {
        "age": age,
        "gender": gender,
        "activity": activity_level
    }).fetchone()

    if not rda:
        raise HTTPException(
            status_code=404,
            detail="No RDA standards found for your profile"
        )

    # Find nutrient gaps (below 80% of RDA)
    nutrients_to_check = [
        {"name": "energy",   "consumed": totals[0], "target": rda[0], "unit": "kcal"},
        {"name": "protein",  "consumed": totals[1], "target": rda[1], "unit": "g"},
        {"name": "calcium",  "consumed": totals[2], "target": rda[2], "unit": "mg"},
        {"name": "iron",     "consumed": totals[3], "target": rda[3], "unit": "mg"},
        {"name": "vitc",     "consumed": totals[4], "target": rda[4], "unit": "mg"},
    ]

    gaps = []
    for n in nutrients_to_check:
        if n["target"] and n["target"] > 0:
            pct = (n["consumed"] / n["target"]) * 100
            if pct < 80:
                gaps.append({
                    "nutrient": n["name"],
                    "percentage": round(pct, 1),
                    "consumed": round(n["consumed"], 1),
                    "target": n["target"],
                    "unit": n["unit"]
                })

    if not gaps:
        return {
            "message": "Great job! You have met 80% or more of all your nutrient targets today.",
            "recommendations": []
        }

    # ICMR DGI 2024 tips per nutrient
    icmr_tips = {
        "energy":  "Include more whole grains like rice, roti, or millets in your meals",
        "protein": "Add a serving of dal, legumes, paneer, eggs, or lean meat to your next meal",
        "calcium": "Include milk, curd, paneer, or green leafy vegetables to boost calcium",
        "iron":    "Include green leafy vegetables, rajma, chana, or ragi for iron. Pair with Vitamin C foods to improve absorption",
        "vitc":    "Add fresh fruits like amla, guava, or citrus, or vegetables like tomato and capsicum"
    }

    # Column mapping for database query per nutrient
    nutrient_column_map = {
        "energy":  ("energy_kcal", "energy_kcal"),
        "protein": ("protein_g",   "protein_g"),
        "calcium": ("calcium_mg",  "calcium_mg"),
        "iron":    ("iron_mg",     "iron_mg"),
        "vitc":    ("vitc_mg",     "vitc_mg"),
    }

    # Dietary preference filter
    # Vegetarians should not see meat/fish recommendations
    veg_groups_exclude = []
    if dietary_preference == "vegetarian":
        veg_groups_exclude = [
            "Poultry", "Animal Meat", "Marine Fish",
            "Marine Shellfish", "Marine Mollusks",
            "Fresh Water Fish and Shellfish"
        ]

    recommendations = []

    for gap in gaps:
        nutrient_name = gap["nutrient"]
        col_foods, col_recipes = nutrient_column_map[nutrient_name]

        # Find top foods from IFCT for this nutrient
        exclude_clause = ""
        params = {"limit": 5}

        if veg_groups_exclude:
            exclude_clause = "AND food_group NOT IN :excluded"
            params["excluded"] = tuple(veg_groups_exclude)

        top_foods = db.execute(text(f"""
            SELECT food_name, {col_foods}, food_group, source, is_lab_tested
            FROM foods
            WHERE {col_foods} IS NOT NULL
            AND {col_foods} > 0
            {"AND food_group NOT IN :excluded" if veg_groups_exclude else ""}
            ORDER BY {col_foods} DESC
            LIMIT :limit
        """), params).fetchall()

        # Find top recipes from INDB for this nutrient
        top_recipes = db.execute(text(f"""
            SELECT food_name, {col_recipes}, source, is_lab_tested
            FROM recipes
            WHERE {col_recipes} IS NOT NULL
            AND {col_recipes} > 0
            ORDER BY {col_recipes} DESC
            LIMIT 3
        """), {"limit": 3}).fetchall()

        suggested = []
        for f in top_foods:
            suggested.append({
                "food_name": f[0],
                f"{col_foods}_per_100g": round(f[1], 1),
                "food_group": f[2],
                "source": f[3],
                "is_lab_tested": f[4],
                "food_type": "ingredient"
            })

        for r in top_recipes:
            suggested.append({
                "food_name": r[0],
                f"{col_recipes}_per_100g": round(r[1], 1),
                "source": r[2],
                "is_lab_tested": r[3],
                "food_type": "recipe"
            })

        recommendations.append({
            "nutrient": nutrient_name,
            "status": f"{gap['percentage']}% of daily target met ({gap['consumed']} / {gap['target']} {gap['unit']})",
            "icmr_tip": icmr_tips.get(nutrient_name, ""),
            "suggested_foods": suggested
        })

    return {
        "message": f"You have {len(gaps)} nutrient gap(s) today. Here are some suggestions.",
        "dietary_preference": dietary_preference,
        "recommendations": recommendations
    }