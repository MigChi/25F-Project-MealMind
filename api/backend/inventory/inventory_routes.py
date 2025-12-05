from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import db

inventory_bp = Blueprint("inventory_bp", __name__)

@inventory_bp.route("/inventory-items", methods=["GET"])
def get_inventory_items():
    """
    Get all inventory items for a given user.
    Expects query param: user_id
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT ii.UserID,
                   ii.IngredientID,
                   ii.AddedDate,
                   ii.Quantity,
                   ii.Unit,
                   ii.ExpirationDate,
                   ii.Status,
                   i.CategoryID,
                   c.CategoryName
            FROM InventoryItem ii
            JOIN Ingredient i ON ii.IngredientID = i.IngredientID
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID
            WHERE ii.UserID = %s
            ORDER BY ii.ExpirationDate IS NULL, ii.ExpirationDate
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_inventory_items: {e}")
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/inventory-items", methods=["POST"])
def create_inventory_item():
    """
    Add a new inventory item for a user.
    Body JSON: {user_id, ingredient_id, quantity, unit, expiration_date?, status?}
    AddedDate defaults to today's date.
    """
    try:
        data = request.get_json() or {}
        required = ["user_id", "ingredient_id", "quantity", "unit"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        user_id = data["user_id"]
        ingredient_id = data["ingredient_id"]
        quantity = data["quantity"]
        unit = data["unit"]
        expiration_date = data.get("expiration_date")  # 'YYYY-MM-DD' or None
        status = data.get("status", "ok")

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            INSERT INTO InventoryItem (UserID, IngredientID, AddedDate,
                                       Quantity, Unit, ExpirationDate, Status)
            VALUES (%s, %s, CURDATE(), %s, %s, %s, %s)
        """
        cursor.execute(
            query,
            (user_id, ingredient_id, quantity, unit, expiration_date, status),
        )
        conn.commit() # type: ignore
        cursor.close()
        return jsonify({"message": "Inventory item created"}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_inventory_item: {e}")
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/inventory-items/<int:ingredient_id>", methods=["PUT"])
def update_inventory_item(ingredient_id: int):
    """
    Update an existing inventory item for a user.
    Identified by user_id + ingredient_id + added_date (all required).
    Query params: user_id, added_date=YYYY-MM-DD
    Body JSON: any of {quantity, unit, expiration_date, status}
    """
    try:
        user_id = request.args.get("user_id", type=int)
        added_date = request.args.get("added_date")
        if not user_id or not added_date:
            return (
                jsonify(
                    {
                        "error": "user_id and added_date query parameters are required to update an inventory item"
                    }
                ),
                400,
            )

        data = request.get_json() or {}
        fields = []
        params = []
        for field in ["Quantity", "Unit", "ExpirationDate", "Status"]:
            key = field.lower()
            if key in data:
                fields.append(f"{field} = %s")
                params.append(data[key])

        if not fields:
            return jsonify({"error": "No updatable fields provided"}), 400

        params.extend([user_id, ingredient_id, added_date])

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = f"""
            UPDATE InventoryItem
            SET {', '.join(fields)}
            WHERE UserID = %s AND IngredientID = %s AND AddedDate = %s
        """
        cursor.execute(query, tuple(params))
        conn.commit() # type: ignore
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Inventory item not found"}), 404

        return jsonify({"message": "Inventory item updated"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_inventory_item: {e}")
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/inventory-items/<int:ingredient_id>", methods=["DELETE"])
def delete_inventory_item(ingredient_id: int):
    """
    Delete an inventory item for a user.
    Identified by user_id + ingredient_id + added_date (all required).
    Query params: user_id, added_date=YYYY-MM-DD
    """
    try:
        user_id = request.args.get("user_id", type=int)
        added_date = request.args.get("added_date")
        if not user_id or not added_date:
            return (
                jsonify(
                    {
                        "error": "user_id and added_date query parameters are required to delete an inventory item"
                    }
                ),
                400,
            )

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            DELETE FROM InventoryItem
            WHERE UserID = %s AND IngredientID = %s AND AddedDate = %s
        """
        cursor.execute(query, (user_id, ingredient_id, added_date))
        conn.commit() # type: ignore
        cursor.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Inventory item not found"}), 404

        return jsonify({"message": "Inventory item deleted"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in delete_inventory_item: {e}")
        return jsonify({"error": str(e)}), 500


@inventory_bp.route("/inventory-items/expiring", methods=["GET"])
def get_expiring_inventory_items():
    """
    Get inventory items for a user that are near or past their expiration date.
    Query params: user_id (required), days_ahead (optional, default 7)
    """
    try:
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            return jsonify({"error": "user_id query parameter is required"}), 400

        days_ahead = request.args.get("days_ahead", default=7, type=int)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT ii.UserID,
                   ii.IngredientID,
                   ii.AddedDate,
                   ii.Quantity,
                   ii.Unit,
                   ii.ExpirationDate,
                   ii.Status,
                   DATEDIFF(ii.ExpirationDate, CURDATE()) AS days_to_expire
            FROM InventoryItem ii
            WHERE ii.UserID = %s
              AND ii.ExpirationDate IS NOT NULL
              AND ii.ExpirationDate <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY ii.ExpirationDate
        """
        cursor.execute(query, (user_id, days_ahead))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_expiring_inventory_items: {e}")
        return jsonify({"error": str(e)}), 500
