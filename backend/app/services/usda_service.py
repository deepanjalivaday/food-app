import os
import httpx
from dotenv import load_dotenv

load_dotenv(r"C:\Users\Avadh\Desktop\musu\food-app\.env")

USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"

def search_usda(query: str, limit: int = 5) -> list:
    """
    Search USDA FoodData Central for foods.
    Called only when local database returns no results.
    """
    try:
        response = httpx.get(
            f"{USDA_BASE_URL}/foods/search",
            params={
                "api_key": USDA_API_KEY,
                "query": query,
                "pageSize": limit,
                "dataType": "Foundation,SR Legacy"
            },
            timeout=10.0
        )

        if response.status_code != 200:
            return []

        data = response.json()
        foods = data.get("foods", [])

        results = []
        for food in foods:
            # Extract nutrients from USDA format
            nutrients = {n["nutrientName"]: n for n in food.get("foodNutrients", [])}

            def get_nutrient(name):
                n = nutrients.get(name)
                return round(n["value"], 2) if n and "value" in n else None

            results.append({
                "id": food.get("fdcId"),
                "food_code": str(food.get("fdcId")),
                "food_name": food.get("description", "").title(),
                "food_group": food.get("foodCategory", ""),
                "source": "usda",
                "is_lab_tested": True,
                "food_type": "ingredient",
                "energy_kcal": get_nutrient("Energy"),
                "protein_g": get_nutrient("Protein"),
                "carb_g": get_nutrient("Carbohydrate, by difference"),
                "fat_g": get_nutrient("Total lipid (fat)"),
                "fibre_g": get_nutrient("Fiber, total dietary"),
                "calcium_mg": get_nutrient("Calcium, Ca"),
                "iron_mg": get_nutrient("Iron, Fe"),
                "sodium_mg": get_nutrient("Sodium, Na"),
                "potassium_mg": get_nutrient("Potassium, K"),
                "zinc_mg": get_nutrient("Zinc, Zn"),
                "vitc_mg": get_nutrient("Vitamin C, total ascorbic acid"),
                "vita_ug": get_nutrient("Vitamin A, RAE"),
                "folate_ug": get_nutrient("Folate, total"),
                "data_source_note": "USDA FoodData Central — US government lab verified"
            })

        return results

    except Exception as e:
        print(f"USDA API error: {e}")
        return []


def get_usda_food_detail(fdc_id: int) -> dict:
    """
    Get full nutrient detail for one USDA food item.
    """
    try:
        response = httpx.get(
            f"{USDA_BASE_URL}/food/{fdc_id}",
            params={"api_key": USDA_API_KEY},
            timeout=10.0
        )

        if response.status_code != 200:
            return {}

        food = response.json()
        nutrients = {n["nutrient"]["name"]: n for n in food.get("foodNutrients", [])}

        def get_nutrient(name):
            n = nutrients.get(name)
            return round(n["amount"], 2) if n and "amount" in n else None

        return {
            "id": food.get("fdcId"),
            "food_code": str(food.get("fdcId")),
            "food_name": food.get("description", "").title(),
            "food_group": food.get("foodCategory", {}).get("description", ""),
            "source": "usda",
            "is_lab_tested": True,
            "food_type": "ingredient",
            "per_100g": {
                "energy_kcal": get_nutrient("Energy"),
                "protein_g": get_nutrient("Protein"),
                "carb_g": get_nutrient("Carbohydrate, by difference"),
                "fat_g": get_nutrient("Total lipid (fat)"),
                "fibre_g": get_nutrient("Fiber, total dietary"),
                "calcium_mg": get_nutrient("Calcium, Ca"),
                "iron_mg": get_nutrient("Iron, Fe"),
                "sodium_mg": get_nutrient("Sodium, Na"),
                "potassium_mg": get_nutrient("Potassium, K"),
                "zinc_mg": get_nutrient("Zinc, Zn"),
                "vitc_mg": get_nutrient("Vitamin C, total ascorbic acid"),
                "vita_ug": get_nutrient("Vitamin A, RAE"),
                "folate_ug": get_nutrient("Folate, total"),
            },
            "data_source_note": "USDA FoodData Central — US government lab verified"
        }

    except Exception as e:
        print(f"USDA API error: {e}")
        return {}