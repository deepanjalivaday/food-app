-- Foods table (raw ingredients from IFCT)
CREATE TABLE IF NOT EXISTS foods (
    id SERIAL PRIMARY KEY,
    food_code VARCHAR(20) UNIQUE,
    food_name VARCHAR(255) NOT NULL,
    aliases TEXT[],
    source VARCHAR(50) DEFAULT 'ifct2017',
    is_lab_tested BOOLEAN DEFAULT TRUE,
    food_group VARCHAR(100),
    energy_kcal FLOAT,
    carb_g FLOAT,
    protein_g FLOAT,
    fat_g FLOAT,
    fibre_g FLOAT,
    calcium_mg FLOAT,
    iron_mg FLOAT,
    sodium_mg FLOAT,
    potassium_mg FLOAT,
    zinc_mg FLOAT,
    vitc_mg FLOAT,
    vita_ug FLOAT,
    folate_ug FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recipes table (composite Indian dishes from INDB)
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    food_code VARCHAR(20) UNIQUE,
    food_name VARCHAR(255) NOT NULL,
    aliases TEXT[],
    source VARCHAR(50) DEFAULT 'indb2024',
    is_lab_tested BOOLEAN DEFAULT FALSE,
    primary_source VARCHAR(100),
    servings_unit VARCHAR(100),
    -- per 100g values
    energy_kj FLOAT,
    energy_kcal FLOAT,
    carb_g FLOAT,
    protein_g FLOAT,
    fat_g FLOAT,
    freesugar_g FLOAT,
    fibre_g FLOAT,
    sfa_mg FLOAT,
    mufa_mg FLOAT,
    pufa_mg FLOAT,
    cholesterol_mg FLOAT,
    calcium_mg FLOAT,
    phosphorus_mg FLOAT,
    magnesium_mg FLOAT,
    sodium_mg FLOAT,
    potassium_mg FLOAT,
    iron_mg FLOAT,
    copper_mg FLOAT,
    selenium_ug FLOAT,
    zinc_mg FLOAT,
    vita_ug FLOAT,
    vite_mg FLOAT,
    vitd2_ug FLOAT,
    vitd3_ug FLOAT,
    vitk1_ug FLOAT,
    folate_ug FLOAT,
    vitb1_mg FLOAT,
    vitb2_mg FLOAT,
    vitb3_mg FLOAT,
    vitb6_mg FLOAT,
    vitc_mg FLOAT,
    carotenoids_ug FLOAT,
    -- per serving values
    unit_serving_energy_kcal FLOAT,
    unit_serving_carb_g FLOAT,
    unit_serving_protein_g FLOAT,
    unit_serving_fat_g FLOAT,
    unit_serving_fibre_g FLOAT,
    unit_serving_calcium_mg FLOAT,
    unit_serving_iron_mg FLOAT,
    unit_serving_vitc_mg FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    weight_kg FLOAT,
    height_cm FLOAT,
    activity_level VARCHAR(20) DEFAULT 'sedentary',
    dietary_preference VARCHAR(20) DEFAULT 'vegetarian',
    health_goals TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Meal logs table
CREATE TABLE IF NOT EXISTS meal_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    food_id INTEGER,
    food_type VARCHAR(10),
    food_name VARCHAR(255),
    quantity_g FLOAT NOT NULL,
    meal_type VARCHAR(20),
    energy_kcal FLOAT,
    protein_g FLOAT,
    carb_g FLOAT,
    fat_g FLOAT,
    fibre_g FLOAT,
    calcium_mg FLOAT,
    iron_mg FLOAT,
    vitc_mg FLOAT,
    logged_at TIMESTAMP DEFAULT NOW()
);

-- Nutrient standards (ICMR RDA 2024)
CREATE TABLE IF NOT EXISTS nutrient_standards (
    id SERIAL PRIMARY KEY,
    age_min INTEGER,
    age_max INTEGER,
    gender VARCHAR(10),
    activity_level VARCHAR(20),
    energy_kcal FLOAT,
    protein_g FLOAT,
    calcium_mg FLOAT,
    iron_mg FLOAT,
    zinc_mg FLOAT,
    vitc_mg FLOAT,
    folate_ug FLOAT,
    vita_ug FLOAT
);