from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date, timedelta
from backend.db_connection import db


profiles_plans_bp = Blueprint("profiles_plans_bp", __name__)


# -------------------------------------------------------------------
# Small helpers to make cursor results predictable (dicts + JSON-safe)
# -------------------------------------------------------------------


def _row_to_dict(columns, row):
    """
    Given a list of column names and a row (tuple or dict), return a clean dict
    and convert date/datetime objects to ISO strings.
    """
    import datetime as _dt

    if isinstance(row, dict):
        out = {}
        for k, v in row.items():
            if isinstance(v, (_dt.date, _dt.datetime)):
                out[k] = v.isoformat()
            else:
                out[k] = v
        return out

    out = {}
    for idx, col in enumerate(columns):
        v = row[idx]
        if isinstance(v, (_dt.date, _dt.datetime)):
            out[col] = v.isoformat()
        else:
            out[col] = v
    return out


def _fetch_one_dict(cursor):
    row = cursor.fetchone()
    if not row:
        return None
    columns = [col[0] for col in cursor.description]
    return _row_to_dict(columns, row)


def _fetch_all_dict(cursor):
    rows = cursor.fetchall()
    if not rows:
        return []
    columns = [col[0] for col in cursor.description]
    return [_row_to_dict(columns, row) for row in rows]


# -------------------------------------------------------------------
# DIET PROFILE  (UsersBudgetProfile)
# -------------------------------------------------------------------


@profiles_plans_bp.route("/diet-profile", methods=["GET"])
def get_diet_profile():
    """
    Get the dietary preference profile for a user.
    Query params: user_id (required)

    Returns JSON:
      {
        "user_id": ...,
        "diet_types": "vegetarian,vegan,high_protein",
        "notes": "..."
      }
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore

        cursor.execute(
            """
            SELECT UserID, DietTypes, Notes
            FROM UsersBudgetProfile
            WHERE UserID = %s
            """,
            (user_id,),
        )
        row = _fetch_one_dict(cursor)
        cursor.close()

        if not row:
            return jsonify({"error": "Diet profile not found"}), 404

        # Normalize keys for the frontend
        result = {
            "user_id": row.get("UserID") or row.get("user_id"),
            "diet_types": row.get("DietTypes") or row.get("diet_types"),
            "notes": row.get("Notes") or row.get("notes"),
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_diet_profile: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/diet-profile", methods=["POST"])
def create_diet_profile():
    """
    Create a new dietary preference profile.

    Body JSON:
      {
        "user_id": 3,
        "diet_types": "vegetarian,high_protein,low_carb",
        "notes": "Any extra constraints"
      }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id")
        diet_types = data.get("diet_types")
        notes = data.get("notes")

        missing = []
        if user_id is None:
            missing.append("user_id")
        if not diet_types:
            missing.append("diet_types")

        if missing:
            return (
                jsonify({"error": f"Missing required fields: {', '.join(missing)}"}),
                400,
            )

        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore

        # Ensure we don't create duplicates
        cursor.execute(
            "SELECT 1 FROM UsersBudgetProfile WHERE UserID = %s", (user_id,)
        )
        if cursor.fetchone():
            cursor.close()
            return (
                jsonify(
                    {"error": "Diet profile already exists. Use PUT to update."}
                ),
                400,
            )

        cursor.execute(
            """
            INSERT INTO UsersBudgetProfile (UserID, DietTypes, Notes)
            VALUES (%s, %s, %s)
            """,
            (user_id, diet_types, notes),
        )
        conn.commit()  # type: ignore
        cursor.close()
        return jsonify({"message": "Diet profile created"}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_diet_profile: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/diet-profile", methods=["PUT"])
def update_diet_profile():
    """
    Update an existing dietary preference profile.

    Body JSON:
      {
        "user_id": 3,                     # required
        "diet_types": "vegetarian,...",   # optional
        "notes": "..."                    # optional
      }
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
        cursor = conn.cursor()  # type: ignore
        query = f"""
            UPDATE UsersBudgetProfile
            SET {', '.join(updates)}
            WHERE UserID = %s
        """
        cursor.execute(query, tuple(params))
        conn.commit()  # type: ignore
        # rowcount may be 0 if values are unchanged; that's still success
        cursor.close()

        return jsonify({"message": "Diet profile updated"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_diet_profile: {e}")
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------
# BUDGET PROFILE  (UserBudgetProfile)
# -------------------------------------------------------------------


@profiles_plans_bp.route("/budget-profile", methods=["GET"])
def get_budget_profile():
    """
    Get the grocery budget profile for a user.
    Query params: user_id (required)

    Returns JSON:
      {
        "user_id": ...,
        "weekly_budget_amount": 80.0,
        "currency": "USD"
      }
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore
        cursor.execute(
            """
            SELECT UserID, WeeklyBudgetAmount, Currency
            FROM UserBudgetProfile
            WHERE UserID = %s
            """,
            (user_id,),
        )
        row = _fetch_one_dict(cursor)
        cursor.close()

        if not row:
            return jsonify({"error": "Budget profile not found"}), 404

        result = {
            "user_id": row.get("UserID") or row.get("user_id"),
            "weekly_budget_amount": row.get("WeeklyBudgetAmount")
            or row.get("weekly_budget_amount"),
            "currency": row.get("Currency") or row.get("currency"),
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_budget_profile: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/budget-profile", methods=["POST"])
def create_budget_profile():
    """
    Create a new grocery budget profile.

    Body JSON:
      {
        "user_id": 3,
        "weekly_budget_amount": 80.0,
        "currency": "USD"
      }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id")
        amount = data.get("weekly_budget_amount", data.get("weekly_budget"))
        currency = data.get("currency")

        missing = []
        if user_id is None:
            missing.append("user_id")
        if amount is None:
            missing.append("weekly_budget_amount")
        if not currency:
            missing.append("currency")

        if missing:
            return (
                jsonify({"error": f"Missing required fields: {', '.join(missing)}"}),
                400,
            )

        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore

        cursor.execute(
            "SELECT 1 FROM UserBudgetProfile WHERE UserID = %s", (user_id,)
        )
        if cursor.fetchone():
            cursor.close()
            return (
                jsonify(
                    {"error": "Budget profile already exists. Use PUT to update."}
                ),
                400,
            )

        cursor.execute(
            """
            INSERT INTO UserBudgetProfile (UserID, WeeklyBudgetAmount, Currency)
            VALUES (%s, %s, %s)
            """,
            (user_id, amount, currency),
        )
        conn.commit()  # type: ignore
        cursor.close()
        return jsonify({"message": "Budget profile created"}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_budget_profile: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/budget-profile", methods=["PUT"])
def update_budget_profile():
    """
    Update an existing budget profile.

    Body JSON:
      {
        "user_id": 3,                   # required
        "weekly_budget_amount": 90.0,   # optional
        "currency": "USD"               # optional
      }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        updates = []
        params = []

        if "weekly_budget_amount" in data or "weekly_budget" in data:
            updates.append("WeeklyBudgetAmount = %s")
            params.append(
                data.get("weekly_budget_amount", data.get("weekly_budget"))
            )
        if "currency" in data:
            updates.append("Currency = %s")
            params.append(data["currency"])

        if not updates:
            return jsonify({"error": "No updatable fields provided"}), 400

        params.append(user_id)

        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore
        query = f"""
            UPDATE UserBudgetProfile
            SET {', '.join(updates)}
            WHERE UserID = %s
        """
        cursor.execute(query, tuple(params))
        conn.commit()  # type: ignore
        # rowcount may be 0 if nothing actually changed; treat as success
        cursor.close()

        return jsonify({"message": "Budget profile updated"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_budget_profile: {e}")
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------
# MEAL PLANS (MealPlan, MealPlanEntry)
# -------------------------------------------------------------------


@profiles_plans_bp.route("/meal-plans", methods=["GET"])
def get_meal_plans():
    """
    List meal plans for a user.
    Query params:
      - user_id (required)
      - current_only (optional, bool-like 'true'/'false')

    Returns a list of:
      {
        "MealPlanID": ...,
        "UserID": ...,
        "StartDate": "YYYY-MM-DD",
        "EndDate": "YYYY-MM-DD",
        "IsSaved": 1/0
      }
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        current_only = (
            request.args.get("current_only", default="false").lower() == "true"
        )

        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore
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
        rows = _fetch_all_dict(cursor)
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_meal_plans: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/meal-plans", methods=["POST"])
def create_meal_plan():
    """
    Create a new meal plan and optional entries.

    Frontend (Jordan page) sends something like:
      {
        "user_id": 3,
        "start_date": "2025-12-07",
        "meals_per_day": 3,
        "respect_budget": true,
        "include_leftovers": true
      }

    This endpoint:
      - Computes end_date = start_date + 6 days if not provided.
      - Auto-generates MealPlanEntry rows if "entries" not provided.
      - Assigns random active recipes to entries that have no recipe_id.
    """
    try:
        data = request.get_json() or {}

        user_id = data.get("user_id")
        start_date_str = data.get("start_date")
        end_date_str = data.get("end_date")  # optional
        meals_per_day = int(data.get("meals_per_day", 3))
        is_saved = bool(data.get("is_saved", True))
        entries = data.get("entries")  # optional manual entries

        missing = []
        if user_id is None:
            missing.append("user_id")
        if not start_date_str:
            missing.append("start_date")

        if missing:
            return (
                jsonify({"error": f"Missing required fields: {', '.join(missing)}"}),
                400,
            )

        # Parse start date
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()  # type: ignore

        # Derive end date if not provided (7-day plan)
        if not end_date_str:
            end_dt = start_dt + timedelta(days=6)
            end_date_str = end_dt.isoformat()
        else:
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # If no entries given, auto-generate simple placeholders
        if entries is None:
            meal_types = ["Breakfast", "Lunch", "Dinner"][:meals_per_day]
            entries = []
            for offset in range((end_dt - start_dt).days + 1):
                day = start_dt + timedelta(days=offset)
                for meal_type in meal_types:
                    entries.append(
                        {
                            "date": day.isoformat(),
                            "meal_type": meal_type,
                            "recipe_id": None,
                            "notes": "",
                        }
                    )

        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore

        # Grab a pool of active recipes and assign them randomly
        cursor.execute(
            """
            SELECT RecipeId
            FROM Recipe
            WHERE Status = 'Active'
            """
        )
        recipe_rows = _fetch_all_dict(cursor)
        recipe_ids = [
            r.get("RecipeId") for r in recipe_rows
            if r.get("RecipeId") is not None
        ]

        if recipe_ids:
            import random

            for entry in entries:
                if entry.get("recipe_id") is None:
                    entry["recipe_id"] = random.choice(recipe_ids)

        # Generate next MealPlanID
        cursor.execute(
            "SELECT COALESCE(MAX(MealPlanID), 0) + 1 AS next_id FROM MealPlan"
        )
        next_id_row = _fetch_one_dict(cursor)
        meal_plan_id = next_id_row.get("next_id") if next_id_row else 1

        # Insert plan
        cursor.execute(
            """
            INSERT INTO MealPlan (MealPlanID, UserID, StartDate, EndDate, IsSaved)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (meal_plan_id, user_id, start_date_str, end_date_str, 1 if is_saved else 0),
        )

        # Insert entries
        for entry in entries:
            cursor.execute(
                """
                INSERT INTO MealPlanEntry
                    (MealPlanID, Date, MealType, RecipeID, Notes)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    meal_plan_id,
                    entry.get("date"),
                    entry.get("meal_type"),
                    entry.get("recipe_id"),
                    entry.get("notes"),
                ),
            )

        conn.commit()  # type: ignore
        cursor.close()

        return jsonify({"message": "Meal plan created", "meal_plan_id": meal_plan_id}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_meal_plan: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/meal-plans/<int:meal_plan_id>", methods=["GET"])
def get_meal_plan_detail(meal_plan_id: int):
    """
    Get details of a single meal plan with its entries.

    Returns:
      {
        "MealPlanID": ...,
        "UserID": ...,
        "StartDate": "YYYY-MM-DD",
        "EndDate": "YYYY-MM-DD",
        "IsSaved": 1/0,
        "entries": [
          {
            "MealPlanID": ...,
            "Date": "YYYY-MM-DD",
            "MealType": "Breakfast",
            "RecipeID": 1,
            "Notes": "...",
            "RecipeName": "Oatmeal with Berries"
          },
          ...
        ]
      }
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore

        # Fetch plan header
        cursor.execute(
            """
            SELECT MealPlanID, UserID, StartDate, EndDate, IsSaved
            FROM MealPlan
            WHERE MealPlanID = %s
            """,
            (meal_plan_id,),
        )
        plan = _fetch_one_dict(cursor)
        if not plan:
            cursor.close()
            return jsonify({"error": "Meal plan not found"}), 404

        # Fetch entries, joined with recipes for RecipeName
        cursor.execute(
            """
            SELECT e.MealPlanID,
                   e.Date,
                   e.MealType,
                   e.RecipeID,
                   e.Notes,
                   r.Name AS RecipeName
            FROM MealPlanEntry e
            LEFT JOIN Recipe r ON e.RecipeID = r.RecipeId
            WHERE e.MealPlanID = %s
            ORDER BY e.Date, e.MealType
            """,
            (meal_plan_id,),
        )
        entries = _fetch_all_dict(cursor)
        cursor.close()

        plan["entries"] = entries
        return jsonify(plan), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_meal_plan_detail: {e}")
        return jsonify({"error": str(e)}), 500


@profiles_plans_bp.route("/meal-plans/<int:meal_plan_id>", methods=["DELETE"])
def delete_meal_plan(meal_plan_id: int):
    """
    Delete a meal plan and all its entries.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore

        # Delete entries first
        cursor.execute(
            "DELETE FROM MealPlanEntry WHERE MealPlanID = %s",
            (meal_plan_id,),
        )
        # Delete the plan itself
        cursor.execute(
            "DELETE FROM MealPlan WHERE MealPlanID = %s",
            (meal_plan_id,),
        )
        conn.commit()  # type: ignore
        affected = cursor.rowcount
        cursor.close()

        if affected == 0:
            return jsonify({"error": "Meal plan not found"}), 404

        return jsonify({"message": "Meal plan deleted"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in delete_meal_plan: {e}")
        return jsonify({"error": str(e)}), 500


