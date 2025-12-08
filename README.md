# MealMind – Inventory-Aware Meal Planning


MealMind is a simple, student-friendly meal planning app built for Northeastern’s **CS 3200** course.


Instead of making you scroll through endless recipe sites, MealMind looks at the ingredients you already have and suggests quick meals based on:


- What is in your inventory right now  
- Your dietary preferences  
- What is close to expiring  
- Your weekly grocery budget (for certain personas)


The goal is to answer the everyday question:


> “What can I make right now?”


Most meal-planning tools are either over-complicated or require too much manual setup. A lot of us buy groceries, forget what we bought, and then throw away food we never get around to cooking.


MealMind tries to fix that by:


- Tracking your ingredients (per user/persona)  
- Suggesting simple, realistic recipes  
- Surfacing food-waste warnings (expiring items)  
- Providing analytics on what tends to get wasted  


It is aimed at busy students, young adults living on their own, beginner cooks who want more confidence, and the “behind-the-scenes” roles (admins and analysts) who keep the system and data healthy.


---


## Team


- **Miguel Chica**  
- **Sam Mollineaux**


---


## High-Level Architecture


This project is organized as a small, containerized full-stack system:


- **MySQL database** (Docker service: `db`)  
  - Schema and mock data are provided via SQL files.
- **Flask REST API** (Docker service: `api`)  
  - Exposes routes for inventory, recipes, profiles, meal plans, ingredients, and analytics.  
  - Uses multiple Blueprints under `api/backend`.
- **Streamlit frontend** (Docker service: `app`)  
  - Implements four personas and calls the API at `http://api:4000`.  
  - Pages live in `app/src/pages`, with shared UI code in `app/src/modules`.


At a high level:


```text
[Streamlit app]  -->  [Flask API]  -->  [MySQL DB]
      app               api               db
```


---


## Personas and Flows


The app is built around four personas, each with their own screens and typical flows:


### Ava – Busy Student Cook


- Manages “My Fridge” inventory  
- Logs weekly groceries  
- Finds quick recipes using what is already in the fridge  
- Marks items as used or expiring  
- Favorites recipes for later  


### Jordan – Health-Focused Professional


- Sets diet preferences and weekly grocery budget  
- Generates weekly meal plans based on constraints  
- Browses budget-friendly recipes that match cost and difficulty  


### Maya – System Administrator


- Manages recipes (add, update, remove)  
- Monitors data quality issues (orphan rows, unused ingredients)  
- Monitors system metrics and alerts, and can create manual alerts  


### Samuel – Data Analyst


- Studies food-waste statistics by ingredient and segment  
- Views recipe usage trends by category  
- Compares behavior across demographic segments and generates reports  


---


## Repository Layout


From the project root:


```text
.
├── api
│   └── backend
│       ├── analytics          # /analytics/... routes
│       ├── db_connection      # MySQL connection helper
│       ├── ingredient         # /categories, /ingredients routes
│       ├── inventory          # /inventory-items routes
│       ├── profiles_plans     # diet, budget, meal plans routes
│       ├── recipes            # recipes + favorite-recipes routes
│       └── simple             # health check, simple test routes
├── app
│   └── src
│       ├── .streamlit         # Streamlit config
│       ├── assets             # Logo and other static assets
│       ├── modules            # Shared UI (e.g., nav sidebar)
│       └── pages              # Persona pages and feature screens
├── database-files             # SQL schema and mock data
├── datasets                   # Any CSVs or external dataset files
├── docs                       # Design docs, diagrams, and notes
├── docker-compose.yml
└── README.md
```


---


## Prerequisites


To run the full system with Docker Compose, you will need:


- Docker and Docker Compose  
- A valid `.env` file in the project root (same folder as `docker-compose.yml`)


You do not need to install Python or MySQL on your host machine; those run inside containers.


---


## Environment Configuration (`.env`)


Create a file named `.env` in the project root (same level as `docker-compose.yml`).


At minimum, include:


```env
# MySQL database config
DB_USER=root
MYSQL_ROOT_PASSWORD=Secret_Password123
DB_HOST=db
DB_PORT=3306
DB_NAME=mealmind


# Flask secret key
SECRET_KEY=someCrazyS3cR3T!Key.!
```


---


## Database Initialization


The MySQL container is seeded using the SQL files located under:


```text
database-files/
    01_mealmind_db.sql     # schema (tables, constraints, etc.)
    02_mock_data.sql       # sample data for personas and analytics
```


In `docker-compose.yml`, the `db` service should be configured so that these files are run automatically on first startup (typically via a `docker-entrypoint-initdb.d` mount).


As long as:


- The SQL scripts are correctly mounted, and  
- The database credentials in `.env` match the compose file  


the schema and mock data will be created when the `db` container starts for the first time.


---


## Running the Project with Docker Compose


From the project root:


1. **Create `.env`**  
   Make sure you have a valid `.env` file as described above.


2. **Build and start all services**


   ```bash
   docker compose up -d
   ```


   This should start three main containers:


   - `db` (MySQL)  
   - `api` (Flask REST API, typically on port 4000)  
   - `app` (Streamlit frontend, typically on port 8501)


3. **Check container status**


   ```bash
   docker compose ps
   ```


4. **Access the app**


   By default, Streamlit runs on:


   ```text
   http://localhost:8501
   ```


   The frontend talks to the API at `http://api:4000` inside the Docker network, and the API talks to MySQL at `db:3306`.


---


## Services and Key Endpoints


### Flask API


The API is defined under `api/backend` and uses multiple Blueprints:


- `simple_routes` – basic health endpoints (for example `/` and `/health`)  
- `inventory_bp` – `/inventory-items`, `/inventory-items/{ingredient_id}`, `/inventory-items/expiring`  
- `recipes_bp` – `/recipes`, `/recipes/{id}`, `/recipes/suggestions`, `/favorite-recipes`  
- `profiles_plans_bp` – `/diet-profile`, `/budget-profile`, `/meal-plans`, `/meal-plans/{id}`  
- `analytics_bp` – `/analytics/waste-statistics`, `/analytics/recipe-usage-statistics`,  
  `/analytics/demographic-segments`, `/analytics/data-quality-reports`,  
  `/analytics/system-metrics`, `/analytics/system-alerts`, `/analytics/system-alerts/{id}`,  
  and `/analytics/reports`  
- `ingredients_bp` – `/categories`, `/ingredients`, `/ingredients/{id}`  


The API base URL used by the Streamlit app inside Docker is:


```text
http://api:4000
```


If you want to call it directly from your host machine, check the port mapping in `docker-compose.yml` (commonly `localhost:4000`).


### Streamlit Frontend


The frontend lives under `app/src`:


- `app/src/pages/Home.py`  
  Persona selector (Ava, Jordan, Maya, Samuel) with mock user identities.


- `app/src/modules/nav.py`  
  Shared sidebar navigation with persona-aware links and a simple session-based “login” flag.


#### Ava (Student Cook)


- `00_Ava_Home.py` – Persona dashboard  
- `01_Ava_Fridge.py` – Inventory view, expiration alerts, ingredient/category management, quantity edits, remove used items  
- `02_Ava_Quick_Recipes.py` – Quick recipes engine based on inventory and prep time, with favorites  
- `03_Ava_Groceries.py` – Weekly groceries intake using ingredient and category helpers  


#### Jordan (Health-Focused Professional)


- `10_Jordan_Home.py` – Persona dashboard  
- `11_Jordan_Preferences.py` – Diet and budget profile management (diet types, notes, weekly budget, currency)  
- `12_Jordan_MealPlan.py` – Weekly meal plan generation and browsing saved plans (including delete)  
- `13_Jordan_Budget_Recipes.py` – Budget-friendly recipes filtered by maximum cost and difficulty  


#### Maya (System Administrator)


- `20_Maya_Home.py` – Persona dashboard  
- `21_Maya_Recipe_Management.py` – Add, update, and delete recipes  
- `22_Maya_Data_Quality.py` – Data quality monitor (orphan inventory items, unused ingredients, recipes with no ingredients)  
- `23_Maya_System_Health.py` – System metrics and alerts (view, acknowledge, resolve, create manual alerts)  


#### Samuel (Data Analyst)


- `30_Samuel_Home.py` – Persona dashboard  
- `31_Samuel_Waste_Analytics.py` – Food waste analytics (by ingredient, category, time period, demographic segment)  
- `32_Samuel_Recipe_Trends.py` – Recipe usage trends by category  
- `33_Samuel_User_Behavior.py` – Demographic segments and combined analytics reports  


- `34_About.py` – About page describing the project, its purpose, and the technical stack.


---


## Development Notes


Some implementation details and design choices:


### Environment and Config


- Flask uses `python-dotenv` to load environment variables from `.env`.  
- Database connection management is centralized in `api/backend/db_connection`.


### Inventory Behavior


- Inventory entries are keyed by `(UserID, IngredientID, AddedDate)`.  
- When a user adds the same ingredient on the same day, the API can merge quantities instead of failing with a duplicate key error.  
- There is a dedicated route for expiring items (`/inventory-items/expiring`) used by Ava’s “My Fridge” page.


### Ingredient and Category Management


- Categories can be created by name, or reused if they already exist.  
- Ingredients can be created with either `category_id` or `category_name`, and the API will look up or create the category as needed.  
- Ingredients can later be updated to change their category.


### Profiles and Plans


- Diet profiles and budget profiles are stored separately.  
- Meal plans are stored with a date range and a set of entries (date, meal type, recipe, notes).  
- When the frontend requests a new plan, the backend can auto-generate entries for a week based on the requested settings.


### Analytics


- Separate tables and routes support data quality reports, food waste statistics, recipe usage statistics, demographic segments, system metrics, and system alerts.  
- The data is mocked but structured to be realistic enough for basic analytics demos.


---


## How to Reset the Database


If you need to completely reset the database to the initial schema and mock data:


1. **Stop containers:**


   ```bash
   docker compose down
   ```


2. **Start everything again:**


   ```bash
   docker compose up -d
   ```


This will re-run the SQL scripts in `database-files/` and restore the original state.