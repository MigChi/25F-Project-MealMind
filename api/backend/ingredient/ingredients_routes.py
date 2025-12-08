from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import db


ingredients_bp = Blueprint("ingredients_bp", __name__)




# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------




def _get_single_value(row, key_if_dict, index_if_tuple=0):
    """Helper to read either a dict row or tuple row safely."""
    if row is None:
        return None
    if isinstance(row, dict):
        return row.get(key_if_dict)
    return row[index_if_tuple]




# ---------------------------------------------------------
# CATEGORIES
# ---------------------------------------------------------




@ingredients_bp.route("/categories", methods=["GET"])
def get_categories():
    """
    Return all categories.


    Response: list of rows with
      { "CategoryID": ..., "CategoryName": ... }
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore
        cursor.execute(
            """
            SELECT CategoryID, CategoryName
            FROM Category
            ORDER BY CategoryName
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_categories: {e}")
        return jsonify({"error": str(e)}), 500




@ingredients_bp.route("/categories", methods=["POST"])
def create_category():
    """
    Create a new category.


    Body JSON:
      { "category_name": "Produce" }


    Returns:
      { "message": "...", "category_id": X }
    """
    try:
        data = request.get_json() or {}
        category_name = (data.get("category_name") or "").strip()


        if not category_name:
            return jsonify({"error": "category_name is required"}), 400


        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore


        # If it already exists, just return the existing ID
        cursor.execute(
            "SELECT CategoryID FROM Category WHERE CategoryName = %s",
            (category_name,),
        )
        existing = cursor.fetchone()
        if existing:
            cat_id = _get_single_value(existing, "CategoryID", 0)
            cursor.close()
            return (
                jsonify(
                    {
                        "message": "Category already exists",
                        "category_id": cat_id,
                    }
                ),
                200,
            )


        # Generate next CategoryID
        cursor.execute(
            "SELECT COALESCE(MAX(CategoryID), 0) + 1 AS next_id FROM Category"
        )
        row = cursor.fetchone()
        category_id = _get_single_value(row, "next_id", 0)


        cursor.execute(
            """
            INSERT INTO Category (CategoryID, CategoryName)
            VALUES (%s, %s)
            """,
            (category_id, category_name),
        )
        conn.commit()  # type: ignore
        cursor.close()


        return (
            jsonify(
                {
                    "message": "Category created",
                    "category_id": category_id,
                }
            ),
            201,
        )
    except Exception as e:
        current_app.logger.error(f"Error in create_category: {e}")
        return jsonify({"error": str(e)}), 500




# ---------------------------------------------------------
# INGREDIENTS
# ---------------------------------------------------------




@ingredients_bp.route("/ingredients", methods=["GET"])
def get_ingredients():
    """
    Get all ingredients, optionally filtered by category_id.


    Query params:
      - category_id (optional)


    Response rows:
      {
        "IngredientID": ...,
        "CategoryID": ...,
        "CategoryName": "Produce" | ...
      }
    """
    try:
        category_id = request.args.get("category_id", type=int)


        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore


        base_query = """
            SELECT
                i.IngredientID,
                i.CategoryID,
                c.CategoryName
            FROM Ingredient i
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID
        """
        params = []
        if category_id is not None:
            base_query += " WHERE i.CategoryID = %s"
            params.append(category_id)


        base_query += " ORDER BY i.IngredientID"


        cursor.execute(base_query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_ingredients: {e}")
        return jsonify({"error": str(e)}), 500




@ingredients_bp.route("/ingredients", methods=["POST"])
def create_ingredient():
    """
    Create a new ingredient.


    Body JSON (flexible):
      {
        # optional, auto-generated if omitted:
        # "ingredient_id": 123,


        # EITHER:
        "category_id": 1,
        # OR:
        "category_name": "Produce"
      }


    - If category_id is provided, it is used directly.
    - If only category_name is provided, this endpoint will:
        * look up an existing Category row by that name, or
        * create a new Category and use its ID.


    Returns:
      {
        "message": "Ingredient created",
        "ingredient_id": ...,
        "category_id": ...
      }
    """
    try:
        data = request.get_json() or {}


        ingredient_id = data.get("ingredient_id")
        category_id = data.get("category_id")
        category_name = (data.get("category_name") or "").strip()


        # You must provide at least one way to identify the category
        if category_id is None and not category_name:
            return (
                jsonify(
                    {
                        "error": "Must provide either category_id or category_name"
                    }
                ),
                400,
            )


        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore


        # If we only got category_name, resolve it to a CategoryID
        if category_id is None and category_name:
            # Look for existing category
            cursor.execute(
                "SELECT CategoryID FROM Category WHERE CategoryName = %s",
                (category_name,),
            )
            row = cursor.fetchone()
            if row:
                category_id = _get_single_value(row, "CategoryID", 0)
            else:
                # Create a new Category
                cursor.execute(
                    "SELECT COALESCE(MAX(CategoryID), 0) + 1 AS next_id FROM Category"
                )
                row2 = cursor.fetchone()
                category_id = _get_single_value(row2, "next_id", 0)


                cursor.execute(
                    """
                    INSERT INTO Category (CategoryID, CategoryName)
                    VALUES (%s, %s)
                    """,
                    (category_id, category_name),
                )


        # Auto-generate IngredientID if not provided
        if ingredient_id is None:
            cursor.execute(
                "SELECT COALESCE(MAX(IngredientID), 0) + 1 AS next_id FROM Ingredient"
            )
            row = cursor.fetchone()
            ingredient_id = _get_single_value(row, "next_id", 0)


        # Check if ingredient already exists with that ID
        cursor.execute(
            "SELECT 1 FROM Ingredient WHERE IngredientID = %s",
            (ingredient_id,),
        )
        if cursor.fetchone():
            cursor.close()
            return (
                jsonify({"error": "Ingredient with that ID already exists."}),
                400,
            )


        # Finally insert the Ingredient row
        cursor.execute(
            """
            INSERT INTO Ingredient (IngredientID, CategoryID)
            VALUES (%s, %s)
            """,
            (ingredient_id, category_id),
        )


        conn.commit()  # type: ignore
        cursor.close()


        return (
            jsonify(
                {
                    "message": "Ingredient created",
                    "ingredient_id": ingredient_id,
                    "category_id": category_id,
                }
            ),
            201,
        )
    except Exception as e:
        current_app.logger.error(f"Error in create_ingredient: {e}")
        return jsonify({"error": str(e)}), 500




@ingredients_bp.route("/ingredients/<int:ingredient_id>", methods=["PUT"])
def update_ingredient(ingredient_id: int):
    """
    Update an ingredient's category.


    Body JSON (any of):
      {
        "category_id": 2,
        "category_name": "New Category Name"
      }


    If neither is provided, this is treated as a no-op: 200, no fields updated.
    """
    try:
        data = request.get_json() or {}
        category_id = data.get("category_id")
        category_name = (data.get("category_name") or "").strip()


        # If neither provided, do nothing but don't error out
        if category_id is None and not category_name:
            return jsonify({"message": "No fields updated (nothing provided)"}), 200


        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore


        # Resolve category_name -> CategoryID if needed
        if category_id is None and category_name:
            cursor.execute(
                "SELECT CategoryID FROM Category WHERE CategoryName = %s",
                (category_name,),
            )
            row = cursor.fetchone()
            if row:
                category_id = _get_single_value(row, "CategoryID", 0)
            else:
                cursor.execute(
                    "SELECT COALESCE(MAX(CategoryID), 0) + 1 AS next_id FROM Category"
                )
                row2 = cursor.fetchone()
                category_id = _get_single_value(row2, "next_id", 0)


                cursor.execute(
                    """
                    INSERT INTO Category (CategoryID, CategoryName)
                    VALUES (%s, %s)
                    """,
                    (category_id, category_name),
                )


        # If after all this we *still* don't have a category_id, bail
        if category_id is None:
            cursor.close()
            return jsonify({"error": "Could not resolve category"}), 400


        cursor.execute(
            """
            UPDATE Ingredient
            SET CategoryID = %s
            WHERE IngredientID = %s
            """,
            (category_id, ingredient_id),
        )
        conn.commit()  # type: ignore
        affected = cursor.rowcount
        cursor.close()


        if affected == 0:
            return jsonify({"error": "Ingredient not found"}), 404


        return jsonify({"message": "Ingredient updated", "category_id": category_id}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_ingredient: {e}")
        return jsonify({"error": str(e)}), 500




@ingredients_bp.route("/ingredients/<int:ingredient_id>", methods=["DELETE"])
def delete_ingredient(ingredient_id: int):
    """
    Delete an ingredient by ID.


    NOTE: This will fail if there are foreign key references
    (e.g. RecipeIngredient, InventoryItem) unless ON DELETE rules are set.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor()  # type: ignore
        cursor.execute(
            "DELETE FROM Ingredient WHERE IngredientID = %s",
            (ingredient_id,),
        )
        conn.commit()  # type: ignore
        affected = cursor.rowcount
        cursor.close()


        if affected == 0:
            return jsonify({"error": "Ingredient not found"}), 404


        return jsonify({"message": "Ingredient deleted"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in delete_ingredient: {e}")
        return jsonify({"error": str(e)}), 500


