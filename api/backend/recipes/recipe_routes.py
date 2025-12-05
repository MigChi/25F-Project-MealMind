from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import db

recipes_bp = Blueprint("recipes_bp", __name__)

@recipes_bp.route("/recipes", methods=["GET"])
def get_recipes():
    """
    List recipes with optional filters.
    Query params: category_id, difficulty, status
    """
    try:
        category_id = request.args.get("category_id", type=int)
        difficulty = request.args.get("difficulty")
        status = request.args.get("status")

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT r.RecipeId,
                   r.Name,
                   r.PrepTimeMinutes,
                   r.DifficultyLevel,
                   r.Status,
                   r.CreatedAt,
                   r.LastUpdateAt,
                   COUNT(ri.IngredientID) AS IngredientCount
            FROM Recipe r
            LEFT JOIN RecipeIngredient ri ON r.RecipeId = ri.RecipeID
            WHERE 1=1
        """
        params = []
        if category_id:
            query += """
                AND r.RecipeId IN (
                    SELECT RecipeID FROM RecipeIngredient ri2
                    JOIN Ingredient i2 ON ri2.IngredientID = i2.IngredientID
                    WHERE i2.CategoryID = %s
                )
            """
            params.append(category_id)
        if difficulty:
            query += " AND r.DifficultyLevel = %s"
            params.append(difficulty)
        if status:
            query += " AND r.Status = %s"
            params.append(status)

        query += " GROUP BY r.RecipeId ORDER BY r.CreatedAt DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_recipes: {e}")
        return jsonify({"error": str(e)}), 500


@recipes_bp.route("/recipes", methods=["POST"])
def create_recipe():
    """
    Create a new recipe (admin/system persona).
    Body JSON: {name, prep_time_minutes, difficulty_level, instructions, status?}
    """
    try:
        data = request.get_json() or {}
        required = ["name", "prep_time_minutes", "difficulty_level", "instructions"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        name = data["name"]
        prep_time = data["prep_time_minutes"]
        difficulty = data["difficulty_level"]
        instructions = data["instructions"]
        status = data.get("status", "Active")

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        # Generate next RecipeId since schema does not use AUTO_INCREMENT
        cursor.execute("SELECT COALESCE(MAX(RecipeId), 0) + 1 AS next_id FROM Recipe")
        next_id_row = cursor.fetchone()
        recipe_id = next_id_row["next_id"] if isinstance(next_id_row, dict) else next_id_row[0]

        query = """
            INSERT INTO Recipe
                (RecipeId, Name, PrepTimeMinutes, DifficultyLevel,
                 Instructions, Status, CreatedAt, LastUpdateAt)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(
            query,
            (recipe_id, name, prep_time, difficulty, instructions, status),
        )
        conn.commit() # type: ignore
        cursor.close()

        return jsonify({"message": "Recipe created", "recipe_id": recipe_id}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_recipe: {e}")
        return jsonify({"error": str(e)}), 500


@recipes_bp.route("/recipes/<int:recipe_id>", methods=["GET"])
def get_recipe_detail(recipe_id: int):
    """
    Get full recipe details including ingredients.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        cursor.execute(
            """
            SELECT RecipeId, Name, PrepTimeMinutes, DifficultyLevel,
                   Instructions, Status, CreatedAt, LastUpdateAt
            FROM Recipe
            WHERE RecipeId = %s
            """,
            (recipe_id,),
        )
        recipe = cursor.fetchone()
        if not recipe:
            cursor.close()
            return jsonify({"error": "Recipe not found"}), 404

        cursor.execute(
            """
            SELECT ri.IngredientID,
                   ri.RequiredQuantity,
                   ri.Unit,
                   i.CategoryID,
                   c.CategoryName
            FROM RecipeIngredient ri
            JOIN Ingredient i ON ri.IngredientID = i.IngredientID
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID
            WHERE ri.RecipeID = %s
            """,
            (recipe_id,),
        )
        ingredients = cursor.fetchall()
        cursor.close()

        recipe["ingredients"] = ingredients
        return jsonify(recipe), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_recipe_detail: {e}")
        return jsonify({"error": str(e)}), 500


@recipes_bp.route("/recipes/<int:recipe_id>", methods=["PUT"])
def update_recipe(recipe_id: int):
    """
    Update fields of a recipe.
    Body JSON: any subset of {name, prep_time_minutes, difficulty_level, instructions, status}
    """
    try:
        data = request.get_json() or {}
        field_map = {
            "name": "Name",
            "prep_time_minutes": "PrepTimeMinutes",
            "difficulty_level": "DifficultyLevel",
            "instructions": "Instructions",
            "status": "Status",
        }

        updates = []
        params = []
        for key, column in field_map.items():
            if key in data:
                updates.append(f"{column} = %s")
                params.append(data[key])

        if not updates:
            return jsonify({"error": "No updatable fields provided"}), 400

        params.append(recipe_id)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = f"""
            UPDATE Recipe
            SET {', '.join(updates)}, LastUpdateAt = NOW()
            WHERE RecipeId = %s
        """
        cursor.execute(query, tuple(params))
        conn.commit() # type: ignore
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Recipe not found"}), 404

        return jsonify({"message": "Recipe updated"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_recipe: {e}")
        return jsonify({"error": str(e)}), 500


@recipes_bp.route("/recipes/<int:recipe_id>", methods=["DELETE"])
def deactivate_recipe(recipe_id: int):
    """
    Soft-delete a recipe by marking Status = 'Inactive'.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        cursor.execute(
            "UPDATE Recipe SET Status = 'Inactive', LastUpdateAt = NOW() WHERE RecipeId = %s",
            (recipe_id,),
        )
        conn.commit() # type: ignore
        affected = cursor.rowcount
        cursor.close()

        if affected == 0:
            return jsonify({"error": "Recipe not found"}), 404

        return jsonify({"message": "Recipe deactivated"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in deactivate_recipe: {e}")
        return jsonify({"error": str(e)}), 500


@recipes_bp.route("/recipes/suggestions", methods=["GET"])
def get_recipe_suggestions():
    """
    Suggest recipes based on a user's inventory.
    Query params: user_id (required), max_prep_time (optional, minutes), limit (optional)
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        max_prep_time = request.args.get("max_prep_time", type=int)
        limit = request.args.get("limit", default=10, type=int)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT DISTINCT r.RecipeId,
                            r.Name,
                            r.PrepTimeMinutes,
                            r.DifficultyLevel,
                            r.Status
            FROM Recipe r
            JOIN RecipeIngredient ri ON r.RecipeId = ri.RecipeID
            JOIN InventoryItem ii
              ON ii.IngredientID = ri.IngredientID
             AND ii.UserID = %s
             AND (ii.ExpirationDate IS NULL OR ii.ExpirationDate >= CURDATE())
            WHERE r.Status = 'Active'
        """
        params = [user_id]
        if max_prep_time is not None:
            query += " AND CAST(r.PrepTimeMinutes AS UNSIGNED) <= %s"
            params.append(max_prep_time)

        query += " LIMIT %s"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_recipe_suggestions: {e}")
        return jsonify({"error": str(e)}), 500


@recipes_bp.route("/favorite-recipes", methods=["GET"])
def get_favorite_recipes():
    """
    Get all favorite recipes for a user.
    Query params: user_id (required)
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT fr.UserID,
                   fr.RecipeID,
                   fr.FavoritedDate,
                   r.Name,
                   r.PrepTimeMinutes,
                   r.DifficultyLevel,
                   r.Status
            FROM FavoriteRecipe fr
            JOIN Recipe r ON fr.RecipeID = r.RecipeId
            WHERE fr.UserID = %s
            ORDER BY fr.FavoritedDate DESC
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_favorite_recipes: {e}")
        return jsonify({"error": str(e)}), 500


@recipes_bp.route("/favorite-recipes", methods=["POST"])
def add_favorite_recipe():
    """
    Add a recipe to a user's favorites.
    Body JSON: {user_id, recipe_id}
    """
    try:
        data = request.get_json() or {}
        required = ["user_id", "recipe_id"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        user_id = data["user_id"]
        recipe_id = data["recipe_id"]

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            INSERT INTO FavoriteRecipe (UserID, RecipeID, FavoritedDate)
            VALUES (%s, %s, CURDATE())
        """
        cursor.execute(query, (user_id, recipe_id))
        conn.commit() # type: ignore
        cursor.close()
        return jsonify({"message": "Recipe added to favorites"}), 201
    except Exception as e:
        current_app.logger.error(f"Error in add_favorite_recipe: {e}")
        return jsonify({"error": str(e)}), 500


@recipes_bp.route("/favorite-recipes/<int:recipe_id>", methods=["DELETE"])
def remove_favorite_recipe(recipe_id: int):
    """
    Remove a recipe from a user's favorites.
    Query params: user_id (required)
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            DELETE FROM FavoriteRecipe
            WHERE UserID = %s AND RecipeID = %s
        """
        cursor.execute(query, (user_id, recipe_id))
        conn.commit() # type: ignore
        affected = cursor.rowcount
        cursor.close()

        if affected == 0:
            return jsonify({"error": "Favorite not found"}), 404

        return jsonify({"message": "Recipe removed from favorites"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in remove_favorite_recipe: {e}")
        return jsonify({"error": str(e)}), 500
