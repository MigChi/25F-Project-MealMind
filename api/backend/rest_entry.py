from flask import Flask
from dotenv import load_dotenv
import os
import logging

from backend.db_connection import db

# Blueprints
from backend.simple.simple_routes import simple_routes
from backend.inventory.inventory_routes import inventory_bp
from backend.recipes.recipe_routes import recipes_bp
from backend.profiles_plans.profile_plan_routes import profiles_plans_bp
from backend.analytics.analytics_routes import analytics_bp


def create_app():
    app = Flask(__name__)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info("API startup")

    # Load environment variables from ../.env
    load_dotenv()

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config["MYSQL_DATABASE_USER"] = os.getenv("DB_USER").strip() # type: ignore
    app.config["MYSQL_DATABASE_PASSWORD"] = os.getenv("MYSQL_ROOT_PASSWORD").strip() # type: ignore
    app.config["MYSQL_DATABASE_HOST"] = os.getenv("DB_HOST").strip() # type: ignore
    app.config["MYSQL_DATABASE_PORT"] = int(os.getenv("DB_PORT").strip()) # type: ignore
    app.config["MYSQL_DATABASE_DB"] = os.getenv("DB_NAME").strip() # type: ignore

    app.logger.info("create_app(): starting the database connection")
    db.init_app(app)

    app.logger.info("create_app(): registering blueprints with Flask app object.")
    app.register_blueprint(simple_routes)              # /, /health
    app.register_blueprint(inventory_bp)               # /inventory-items...
    app.register_blueprint(recipes_bp)                 # /recipes..., /favorite-recipes...
    app.register_blueprint(profiles_plans_bp)          # /diet-profile, /budget-profile, /meal-plans...
    app.register_blueprint(analytics_bp)               # /system-metrics, /waste-statistics, etc.

    return app
