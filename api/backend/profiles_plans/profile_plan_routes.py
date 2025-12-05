from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import db

profiles_plans_bp = Blueprint("profiles_plans_bp", __name__)


# ---------------- Diet Profile (UsersBudgetProfile) ------------------


@profiles_plans_bp.route("/diet-profile", methods=["GET"])
def get_diet_profile():
    """
    Get the dietary preference profile for a user.
    Query params: user_id (required)
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        cursor.execute(
            """
            SELECT UserID, DietTypes, Notes
            FROM UsersBudgetProfile
            WHERE UserID = %s
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return jsonify({"error": "Diet profile not found"}), 404
        return jsonify(row), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_diet_profile: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/diet-profile", methods=["POST"])
def create_diet_profile():
    """
    Create a new dietary preference profile.
    Body JSON: {user_id, diet_types, notes?}
    """
    try:
        data = request.get_json() or {}
        required = ["user_id", "diet_types"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        user_id = data["user_id"]
        diet_types = data["diet_types"]
        notes = data.get("notes")

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        # Ensure we don't create duplicates
        cursor.execute(
            "SELECT 1 FROM UsersBudgetProfile WHERE UserID = %s", (user_id,)
        )
        if cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Diet profile already exists. Use PUT to update."}), 400

        cursor.execute(
            """
            INSERT INTO UsersBudgetProfile (UserID, DietTypes, Notes)
            VALUES (%s, %s, %s)
            """,
            (user_id, diet_types, notes),
        )
        conn.commit() # type: ignore
        cursor.close()
        return jsonify({"message": "Diet profile created"}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_diet_profile: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/diet-profile", methods=["PUT"])
def update_diet_profile():
    """
    Update an existing dietary preference profile.
    Body JSON: {user_id, diet_types?, notes?}
    """
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        updates = []
        params = []
        if "diet_types" in data:
            updates.append("DietTypes = %s")
            params.append(data["diet_types"])
        if "notes" in data:
            updates.append("Notes = %s")
            params.append(data["notes"])

        if not updates:
            return jsonify({"error": "No updatable fields provided"}), 400

        params.append(user_id)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = f"""
            UPDATE UsersBudgetProfile
            SET {', '.join(updates)}
            WHERE UserID = %s
        """
        cursor.execute(query, tuple(params))
        conn.commit() # type: ignore
        affected = cursor.rowcount
        cursor.close()

        if affected == 0:
            return jsonify({"error": "Diet profile not found"}), 404

        return jsonify({"message": "Diet profile updated"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_diet_profile: {e}")
        return jsonify({"error": str(e)}), 500


# ---------------- Budget Profile (UserBudgetProfile) ------------------


@profiles_plans_bp.route("/budget-profile", methods=["GET"])
def get_budget_profile():
    """
    Get the grocery budget profile for a user.
    Query params: user_id (required)
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        cursor.execute(
            """
            SELECT UserID, WeeklyBudgetAmount, Currency
            FROM UserBudgetProfile
            WHERE UserID = %s
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return jsonify({"error": "Budget profile not found"}), 404
        return jsonify(row), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_budget_profile: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/budget-profile", methods=["POST"])
def create_budget_profile():
    """
    Create a new grocery budget profile.
    Body JSON: {user_id, weekly_budget_amount, currency}
    """
    try:
        data = request.get_json() or {}
        required = ["user_id", "weekly_budget_amount", "currency"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        user_id = data["user_id"]
        amount = data["weekly_budget_amount"]
        currency = data["currency"]

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        cursor.execute(
            "SELECT 1 FROM UserBudgetProfile WHERE UserID = %s", (user_id,)
        )
        if cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Budget profile already exists. Use PUT to update."}), 400

        cursor.execute(
            """
            INSERT INTO UserBudgetProfile (UserID, WeeklyBudgetAmount, Currency)
            VALUES (%s, %s, %s)
            """,
            (user_id, amount, currency),
        )
        conn.commit() # type: ignore
        cursor.close()
        return jsonify({"message": "Budget profile created"}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_budget_profile: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/budget-profile", methods=["PUT"])
def update_budget_profile():
    """
    Update an existing budget profile.
    Body JSON: {user_id, weekly_budget_amount?, currency?}
    """
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        updates = []
        params = []
        if "weekly_budget_amount" in data:
            updates.append("WeeklyBudgetAmount = %s")
            params.append(data["weekly_budget_amount"])
        if "currency" in data:
            updates.append("Currency = %s")
            params.append(data["currency"])

        if not updates:
            return jsonify({"error": "No updatable fields provided"}), 400

        params.append(user_id)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = f"""
            UPDATE UserBudgetProfile
            SET {', '.join(updates)}
            WHERE UserID = %s
        """
        cursor.execute(query, tuple(params))
        conn.commit() # type: ignore
        affected = cursor.rowcount
        cursor.close()

        if affected == 0:
            return jsonify({"error": "Budget profile not found"}), 404

        return jsonify({"message": "Budget profile updated"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_budget_profile: {e}")
        return jsonify({"error": str(e)}), 500


# ---------------- Meal Plans (MealPlan, MealPlanEntry) ------------------


@profiles_plans_bp.route("/meal-plans", methods=["GET"])
def get_meal_plans():
    """
    List meal plans for a user.
    Query params:
      - user_id (required)
      - current_only (optional, bool-like 'true'/'false')
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        current_only = request.args.get("current_only", default="false").lower() == "true"

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT MealPlanID, UserID, StartDate, EndDate, IsSaved
            FROM MealPlan
            WHERE UserID = %s
        """
        params = [user_id]
        if current_only:
            query += " AND StartDate <= CURDATE() AND EndDate >= CURDATE()"

        query += " ORDER BY StartDate DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_meal_plans: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/meal-plans", methods=["POST"])
def create_meal_plan():
    """
    Create a new meal plan and optional entries.
    Body JSON:
    {
      "user_id": ...,
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "is_saved": true/false,
      "entries": [
        {"date": "YYYY-MM-DD", "meal_type": "Breakfast", "recipe_id": 1, "notes": "..."},
        ...
      ]
    }
    """
    try:
        data = request.get_json() or {}
        required = ["user_id", "start_date", "end_date"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        user_id = data["user_id"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        is_saved = bool(data.get("is_saved", True))
        entries = data.get("entries", [])

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        # Generate next MealPlanID
        cursor.execute("SELECT COALESCE(MAX(MealPlanID), 0) + 1 AS next_id FROM MealPlan")
        next_id_row = cursor.fetchone()
        meal_plan_id = next_id_row["next_id"] if isinstance(next_id_row, dict) else next_id_row[0]

        cursor.execute(
            """
            INSERT INTO MealPlan (MealPlanID, UserID, StartDate, EndDate, IsSaved)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (meal_plan_id, user_id, start_date, end_date, 1 if is_saved else 0),
        )

        # Insert entries if provided
        for entry in entries:
            cursor.execute(
                """
                INSERT INTO MealPlanEntry
                    (MealPlanID, Date, MealType, RecipeID, Notes)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    meal_plan_id,
                    entry["date"],
                    entry["meal_type"],
                    entry.get("recipe_id"),
                    entry.get("notes"),
                ),
            )

        conn.commit() # type: ignore
        cursor.close()
        return jsonify({"message": "Meal plan created", "meal_plan_id": meal_plan_id}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_meal_plan: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/meal-plans/<int:meal_plan_id>", methods=["GET"])
def get_meal_plan_detail(meal_plan_id: int):
    """
    Get details of a single meal plan with its entries.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        cursor.execute(
            """
            SELECT MealPlanID, UserID, StartDate, EndDate, IsSaved
            FROM MealPlan
            WHERE MealPlanID = %s
            """,
            (meal_plan_id,),
        )
        plan = cursor.fetchone()
        if not plan:
            cursor.close()
            return jsonify({"error": "Meal plan not found"}), 404

        cursor.execute(
            """
            SELECT MealPlanID, Date, MealType, RecipeID, Notes
            FROM MealPlanEntry
            WHERE MealPlanID = %s
            ORDER BY Date, MealType
            """,
            (meal_plan_id,),
        )
        entries = cursor.fetchall()
        cursor.close()

        plan["entries"] = entries
        return jsonify(plan), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_meal_plan_detail: {e}")
        return jsonify({"error": str(e)}), 500
