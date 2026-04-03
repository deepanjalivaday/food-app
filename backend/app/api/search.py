from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.services.usda_service import search_usda, get_usda_food_detail

router = APIRouter()

@router.get("/foods/search")
def search_foods(
    q: str = Query(..., min_length=2, description="Food name to search"),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    query = f"%{q.lower()}%"

    # Search foods table (IFCT - raw ingredients)
    foods_result = db.execute(text("""
        SELECT 
            id, food_code, food_name, food_group, source, is_lab_tested,
            energy_kcal, protein_g, carb_g, fat_g, fibre_g,
            calcium_mg, iron_mg, sodium_mg, zinc_mg, vitc_mg,
            CASE 
                WHEN LOWER(food_name) = :exact THEN 1
                WHEN LOWER(food_name) LIKE :starts THEN 2
                WHEN LOWER(food_name) LIKE :query THEN 3
                ELSE 4
            END as rank
        FROM foods
        WHERE LOWER(food_name) LIKE :query
        ORDER BY rank, food_name
        LIMIT :limit
    """), {
        "query": query,
        "exact": q.lower(),
        "starts": f"{q.lower()}%",
        "limit": limit
    }).fetchall()

    # Search recipes table (INDB - composite dishes)
    recipes_result = db.execute(text("""
        SELECT 
            id, food_code, food_name,
            'Indian Recipe' as food_group,
            source, is_lab_tested,
            energy_kcal, protein_g, carb_g, fat_g, fibre_g,
            calcium_mg, iron_mg, sodium_mg, zinc_mg, vitc_mg,
            CASE 
                WHEN LOWER(food_name) = :exact THEN 1
                WHEN LOWER(food_name) LIKE :starts THEN 2
                WHEN LOWER(food_name) LIKE :query THEN 3
                ELSE 4
            END as rank
        FROM recipes
        WHERE LOWER(food_name) LIKE :query
        ORDER BY rank, food_name
        LIMIT :limit
    """), {
        "query": query,
        "exact": q.lower(),
        "starts": f"{q.lower()}%",
        "limit": limit
    }).fetchall()

    # Combine and format results
    results = []

    for row in foods_result:
        results.append({
            "id": row[0],
            "food_code": row[1],
            "food_name": row[2],
            "food_group": row[3],
            "source": row[4],
            "is_lab_tested": row[5],
            "food_type": "ingredient",
            "energy_kcal": round(row[6], 1) if row[6] else None,
            "protein_g": round(row[7], 1) if row[7] else None,
            "carb_g": round(row[8], 1) if row[8] else None,
            "fat_g": round(row[9], 1) if row[9] else None,
            "fibre_g": round(row[10], 1) if row[10] else None,
            "calcium_mg": round(row[11], 1) if row[11] else None,
            "iron_mg": round(row[12], 1) if row[12] else None,
            "sodium_mg": round(row[13], 1) if row[13] else None,
            "zinc_mg": round(row[14], 1) if row[14] else None,
            "vitc_mg": round(row[15], 1) if row[15] else None,
            "rank": row[16]
        })

    for row in recipes_result:
        results.append({
            "id": row[0],
            "food_code": row[1],
            "food_name": row[2],
            "food_group": row[3],
            "source": row[4],
            "is_lab_tested": row[5],
            "food_type": "recipe",
            "energy_kcal": round(row[6], 1) if row[6] else None,
            "protein_g": round(row[7], 1) if row[7] else None,
            "carb_g": round(row[8], 1) if row[8] else None,
            "fat_g": round(row[9], 1) if row[9] else None,
            "fibre_g": round(row[10], 1) if row[10] else None,
            "calcium_mg": round(row[11], 1) if row[11] else None,
            "iron_mg": round(row[12], 1) if row[12] else None,
            "sodium_mg": round(row[13], 1) if row[13] else None,
            "zinc_mg": round(row[14], 1) if row[14] else None,
            "vitc_mg": round(row[15], 1) if row[15] else None,
            "rank": row[16]
        })

    # Sort by rank then remove rank field
    results.sort(key=lambda x: x["rank"])
    for r in results:
        del r["rank"]

    # If no local results found, fall back to USDA
    if len(results) == 0:
        print(f"No local results for '{q}' — trying USDA API...")
        usda_results = search_usda(q, limit)
        if usda_results:
            return {
                "query": q,
                "total": len(usda_results),
                "source_note": "No local Indian food data found — showing USDA results",
                "results": usda_results
            }

    return {
        "query": q,
        "total": len(results),
        "results": results
    }


@router.get("/foods/{food_type}/{food_id}")
def get_food_detail(
    food_type: str,
    food_id: int,
    db: Session = Depends(get_db)
):
    if food_type == "ingredient":
        result = db.execute(text("""
            SELECT 
                id, food_code, food_name, food_group, source, is_lab_tested,
                energy_kcal, protein_g, carb_g, fat_g, fibre_g,
                calcium_mg, iron_mg, sodium_mg, potassium_mg, zinc_mg,
                vitc_mg, vita_ug, folate_ug
            FROM foods
            WHERE id = :id
        """), {"id": food_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Food not found")

        return {
            "id": result[0],
            "food_code": result[1],
            "food_name": result[2],
            "food_group": result[3],
            "source": result[4],
            "is_lab_tested": result[5],
            "food_type": "ingredient",
            "per_100g": {
                "energy_kcal": round(result[6], 1) if result[6] else None,
                "protein_g": round(result[7], 1) if result[7] else None,
                "carb_g": round(result[8], 1) if result[8] else None,
                "fat_g": round(result[9], 1) if result[9] else None,
                "fibre_g": round(result[10], 1) if result[10] else None,
                "calcium_mg": round(result[11], 1) if result[11] else None,
                "iron_mg": round(result[12], 1) if result[12] else None,
                "sodium_mg": round(result[13], 1) if result[13] else None,
                "potassium_mg": round(result[14], 1) if result[14] else None,
                "zinc_mg": round(result[15], 1) if result[15] else None,
                "vitc_mg": round(result[16], 1) if result[16] else None,
                "vita_ug": round(result[17], 1) if result[17] else None,
                "folate_ug": round(result[18], 1) if result[18] else None,
            },
            "data_source_note": "Lab tested by ICMR-NIN across 6 regions of India" if result[5] else "Calculated from ICMR-NIN data"
        }

    elif food_type == "recipe":
        result = db.execute(text("""
            SELECT
                id, food_code, food_name, source, is_lab_tested,
                energy_kcal, protein_g, carb_g, fat_g, fibre_g,
                calcium_mg, iron_mg, sodium_mg, potassium_mg, zinc_mg,
                vitc_mg, vita_ug, folate_ug,
                unit_serving_energy_kcal, unit_serving_protein_g,
                unit_serving_carb_g, unit_serving_fat_g,
                unit_serving_fibre_g, unit_serving_calcium_mg,
                unit_serving_iron_mg, unit_serving_vitc_mg,
                servings_unit, primary_source
            FROM recipes
            WHERE id = :id
        """), {"id": food_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Recipe not found")

        return {
            "id": result[0],
            "food_code": result[1],
            "food_name": result[2],
            "source": result[3],
            "is_lab_tested": result[4],
            "food_type": "recipe",
            "serving_description": result[26],
            "per_100g": {
                "energy_kcal": round(result[5], 1) if result[5] else None,
                "protein_g": round(result[6], 1) if result[6] else None,
                "carb_g": round(result[7], 1) if result[7] else None,
                "fat_g": round(result[8], 1) if result[8] else None,
                "fibre_g": round(result[9], 1) if result[9] else None,
                "calcium_mg": round(result[10], 1) if result[10] else None,
                "iron_mg": round(result[11], 1) if result[11] else None,
                "sodium_mg": round(result[12], 1) if result[12] else None,
                "potassium_mg": round(result[13], 1) if result[13] else None,
                "zinc_mg": round(result[14], 1) if result[14] else None,
                "vitc_mg": round(result[15], 1) if result[15] else None,
                "vita_ug": round(result[16], 1) if result[16] else None,
                "folate_ug": round(result[17], 1) if result[17] else None,
            },
            "per_serving": {
                "energy_kcal": round(result[18], 1) if result[18] else None,
                "protein_g": round(result[19], 1) if result[19] else None,
                "carb_g": round(result[20], 1) if result[20] else None,
                "fat_g": round(result[21], 1) if result[21] else None,
                "fibre_g": round(result[22], 1) if result[22] else None,
                "calcium_mg": round(result[23], 1) if result[23] else None,
                "iron_mg": round(result[24], 1) if result[24] else None,
                "vitc_mg": round(result[25], 1) if result[25] else None,
            },
            "data_source_note": f"Calculated from ICMR-NIN data. Primary source: {result[27]}"
        }

    elif food_type == "usda":
        result = get_usda_food_detail(food_id)
        if not result:
            raise HTTPException(status_code=404, detail="Food not found on USDA")
        return result

    else:
        raise HTTPException(
            status_code=400,
            detail="food_type must be 'ingredient', 'recipe', or 'usda'"
        )