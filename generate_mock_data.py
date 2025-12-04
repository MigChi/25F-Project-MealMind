from faker import Faker
from datetime import datetime, timedelta, date
import random

fake = Faker()

# ------------- CONFIG: HOW MANY ROWS -------------
NUM_CATEGORIES = 30
NUM_SEGMENTS = 30
NUM_INGREDIENTS = 40
NUM_RECIPES = 40
NUM_TIME_PERIODS = 30
NUM_USERS = 40

NUM_RECIPE_INGREDIENTS = 150
NUM_WASTE_STATS = 150
NUM_RECIPE_USAGE_STATS = 150

NUM_INVENTORY_ITEMS = 60
NUM_FAVORITES = 150

NUM_MEAL_PLANS = 40
NUM_MEAL_PLAN_ENTRIES = 150

NUM_SYSTEM_METRICS = 30
NUM_METRIC_SNAPSHOTS = 60
NUM_SYSTEM_ALERTS = 60

# ------------- HELPER FUNCTIONS -------------

def sql_value(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, datetime):
        return f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'"
    if isinstance(v, date):
        return f"'{v.strftime('%Y-%m-%d')}'"
    if isinstance(v, str):
        v = v.replace("'", "''")
        return f"'{v}'"
    v = str(v).replace("'", "''")
    return f"'{v}'"

def insert_stmt(table, row):
    cols = ", ".join(row.keys())
    vals = ", ".join(sql_value(v) for v in row.values())
    return f"INSERT INTO {table} ({cols}) VALUES ({vals});"


# ------------- STRONG ENTITIES -------------

categories = [
    {
        "CategoryID": i,
        "CategoryName": fake.word().title()
    }
    for i in range(1, NUM_CATEGORIES + 1)
]

segments = []
for i in range(1, NUM_SEGMENTS + 1):
    age_min = random.choice([18, 25, 35])
    age_max = age_min + random.choice([10, 15])
    segments.append({
        "SegmentID": i,
        "Name": f"{age_min}-{age_max} {random.choice(['Students', 'Adults', 'Families'])}",
        "AgeMin": age_min,
        "AgeMax": age_max,
        "Region": fake.city()
    })

ingredients = []
for i in range(1, NUM_INGREDIENTS + 1):
    ingredients.append({
        "IngredientID": i,
        "CategoryID": random.randint(1, NUM_CATEGORIES)
    })

recipes = []
for i in range(1, NUM_RECIPES + 1):
    created = fake.date_time_between(start_date="-1y", end_date="now")
    recipes.append({
        "RecipeId": i,
        "Name": fake.sentence(nb_words=3).replace(".", ""),
        "PrepTimeMinutes": random.choice(["15", "20", "30", "45", "60"]),
        "DifficultyLevel": random.choice(["Easy", "Medium", "Hard"]),
        "Instructions": fake.paragraph(nb_sentences=5),
        "Status": random.choice(["Active", "Inactive"]),
        "CreatedAt": created,
        "LastUpdateAt": created + timedelta(days=random.randint(0, 60))
    })

time_periods = []
for i in range(1, NUM_TIME_PERIODS + 1):
    start = fake.date_between(start_date="-6M", end_date="-1M")
    end = start + timedelta(days=30)
    time_periods.append({
        "PeriodID": i,
        "StartDate": start,
        "EndDate": end,
        "Granularity": "Monthly"
    })

users = []
for i in range(1, NUM_USERS + 1):
    first = fake.first_name()
    last = fake.last_name()
    users.append({
        "UserID": i,
        "Email": fake.unique.email(),
        "Region": fake.city(),
        "FName": first,
        "LName": last,
        "Age": random.randint(18, 65)
    })

system_metrics = []
for i in range(1, NUM_SYSTEM_METRICS + 1):
    system_metrics.append({
        "MetricID": i,
        "Name": random.choice(["API Latency", "DB Storage", "Active Users", "Error Rate"]) + f" {i}",
        "Description": fake.sentence()
    })


# ------------- BRIDGE / WEAK TABLES -------------

# RecipeIngredient (PK = RecipeID, IngredientID)
recipe_ing_pairs = set()
recipe_ingredients = []
while len(recipe_ingredients) < NUM_RECIPE_INGREDIENTS:
    rid = random.randint(1, NUM_RECIPES)
    iid = random.randint(1, NUM_INGREDIENTS)
    key = (rid, iid)
    if key in recipe_ing_pairs:
        continue
    recipe_ing_pairs.add(key)
    recipe_ingredients.append({
        "RecipeID": rid,
        "IngredientID": iid,
        "RequiredQuantity": round(random.uniform(0.1, 3.0), 2),
        "Unit": random.choice(["g", "kg", "oz", "lb", "cup", "tbsp", "tsp"])
    })

# WasteStatistic
waste_stats = []
for i in range(1, NUM_WASTE_STATS + 1):
    waste_stats.append({
        "WasteStatID": i,
        "IngredientID": random.randint(1, NUM_INGREDIENTS),
        "PeriodID": random.randint(1, NUM_TIME_PERIODS),
        "SegmentID": random.randint(1, NUM_SEGMENTS),
        "WastedAmount": round(random.uniform(0, 50), 2),
        "WasteRatePercent": round(random.uniform(0, 100), 2)
    })

# RecipeUsageStatistic
recipe_usage_stats = []
for i in range(1, NUM_RECIPE_USAGE_STATS + 1):
    recipe_usage_stats.append({
        "UsageStatID": i,
        "RecipeID": random.randint(1, NUM_RECIPES),
        "PeriodID": random.randint(1, NUM_TIME_PERIODS),
        "SegmentID": random.randint(1, NUM_SEGMENTS),
        "UsageCount": random.randint(0, 200),
        "UniqueUsers": random.randint(0, 100)
    })

# InventoryItem (PK = UserID, IngredientID, AddedDate)
inv_keys = set()
inventory_items = []
while len(inventory_items) < NUM_INVENTORY_ITEMS:
    user_id = random.randint(1, NUM_USERS)
    ingredient_id = random.randint(1, NUM_INGREDIENTS)
    added = fake.date_between(start_date="-30d", end_date="today")
    key = (user_id, ingredient_id, added)
    if key in inv_keys:
        continue
    inv_keys.add(key)
    inventory_items.append({
        "UserID": user_id,
        "IngredientID": ingredient_id,
        "AddedDate": added,
        "Quantity": round(random.uniform(0.1, 5.0), 2),
        "Unit": random.choice(["g", "kg", "oz", "lb", "cup", "tbsp", "tsp"]),
        "ExpirationDate": added + timedelta(days=random.randint(1, 30)),
        "Status": random.choice(["Fresh", "Near Expiry", "Expired"])
    })

# UserBudgetProfile (1 row per user)
user_budget_profiles = []
for u in users:
    user_budget_profiles.append({
        "UserID": u["UserID"],
        "WeeklyBudgetAmount": round(random.uniform(25, 150), 2),
        "Currency": "USD"
    })

# UsersBudgetProfile (diet/preferences)
users_budget_profiles = []
for u in users:
    users_budget_profiles.append({
        "UserID": u["UserID"],
        "DietTypes": random.choice(["None", "Vegetarian", "Vegan", "Gluten Free", "Pescatarian"]),
        "Notes": fake.sentence()
    })

# FavoriteRecipe (PK = UserID, RecipeID)
fav_pairs = set()
favorite_recipes = []
while len(favorite_recipes) < NUM_FAVORITES:
    uid = random.randint(1, NUM_USERS)
    rid = random.randint(1, NUM_RECIPES)
    key = (uid, rid)
    if key in fav_pairs:
        continue
    fav_pairs.add(key)
    favorite_recipes.append({
        "UserID": uid,
        "RecipeID": rid,
        "FavoritedDate": fake.date_between(start_date="-6M", end_date="today")
    })

# MealPlan
meal_plans = []
for i in range(1, NUM_MEAL_PLANS + 1):
    user_id = random.randint(1, NUM_USERS)
    start = fake.date_between(start_date="-30d", end_date="today")
    end = start + timedelta(days=6)
    meal_plans.append({
        "MealPlanID": i,
        "UserID": user_id,
        "StartDate": start,
        "EndDate": end,
        "IsSaved": 1  # tinyint(1)
    })

# MealPlanEntry (PK = MealPlanID, Date, MealType)
entry_keys = set()
meal_plan_entries = []
while len(meal_plan_entries) < NUM_MEAL_PLAN_ENTRIES:
    mp_id = random.randint(1, NUM_MEAL_PLANS)
    day_offset = random.randint(0, 6)
    date_val = date.today() + timedelta(days=day_offset)
    meal_type = random.choice(["Breakfast", "Lunch", "Dinner"])
    key = (mp_id, date_val, meal_type)
    if key in entry_keys:
        continue
    entry_keys.add(key)
    meal_plan_entries.append({
        "MealPlanID": mp_id,
        "Date": date_val,
        "MealType": meal_type,
        "RecipeID": random.randint(1, NUM_RECIPES),
        "Notes": fake.sentence()
    })

# MetricSnapshot
metric_snapshots = []
for i in range(1, NUM_METRIC_SNAPSHOTS + 1):
    metric_id = random.randint(1, NUM_SYSTEM_METRICS)
    measured = fake.date_time_between(start_date="-7d", end_date="now")
    metric_snapshots.append({
        "SnapshotID": i,
        "MetricID": metric_id,
        "MeasuredAt": measured,
        "Value": round(random.uniform(0, 1000), 2)
    })

# SystemAlert
system_alerts = []
for i in range(1, NUM_SYSTEM_ALERTS + 1):
    metric_id = random.choice([None, random.randint(1, NUM_SYSTEM_METRICS)])
    created = fake.date_time_between(start_date="-7d", end_date="now")
    resolved = created + timedelta(hours=random.randint(1, 72)) if random.choice([True, False]) else None
    system_alerts.append({
        "AlertID": i,
        "MetricID": metric_id,
        "AlertType": random.choice(["Threshold", "Error Spike", "Downtime"]),
        "Severity": random.choice(["Low", "Medium", "High", "Critical"]),
        "Message": fake.sentence(),
        "CreatedAt": created,
        "ResolvedAt": resolved,
        "Status": random.choice(["Open", "Acknowledged", "Resolved"])
    })


# ------------- PRINT INSERTS IN FK-SAFE ORDER -------------

print("-- Category")
for r in categories:
    print(insert_stmt("Category", r))

print("\n-- DemographicSegment")
for r in segments:
    print(insert_stmt("DemographicSegment", r))

print("\n-- Ingredient")
for r in ingredients:
    print(insert_stmt("Ingredient", r))

print("\n-- Recipe")
for r in recipes:
    print(insert_stmt("Recipe", r))

print("\n-- TimePeriod")
for r in time_periods:
    print(insert_stmt("TimePeriod", r))

print("\n-- User")
for r in users:
    print(insert_stmt("User", r))

print("\n-- SystemMetric")
for r in system_metrics:
    print(insert_stmt("SystemMetric", r))

print("\n-- WasteStatistic")
for r in waste_stats:
    print(insert_stmt("WasteStatistic", r))

print("\n-- RecipeIngredient")
for r in recipe_ingredients:
    print(insert_stmt("RecipeIngredient", r))

print("\n-- RecipeUsageStatistic")
for r in recipe_usage_stats:
    print(insert_stmt("RecipeUsageStatistic", r))

print("\n-- InventoryItem")
for r in inventory_items:
    print(insert_stmt("InventoryItem", r))

print("\n-- UserBudgetProfile")
for r in user_budget_profiles:
    print(insert_stmt("UserBudgetProfile", r))

print("\n-- UsersBudgetProfile")
for r in users_budget_profiles:
    print(insert_stmt("UsersBudgetProfile", r))

print("\n-- FavoriteRecipe")
for r in favorite_recipes:
    print(insert_stmt("FavoriteRecipe", r))

print("\n-- MealPlan")
for r in meal_plans:
    print(insert_stmt("MealPlan", r))

print("\n-- MealPlanEntry")
for r in meal_plan_entries:
    print(insert_stmt("MealPlanEntry", r))

print("\n-- MetricSnapshot")
for r in metric_snapshots:
    print(insert_stmt("MetricSnapshot", r))

print("\n-- SystemAlert")
for r in system_alerts:
    print(insert_stmt("SystemAlert", r))
