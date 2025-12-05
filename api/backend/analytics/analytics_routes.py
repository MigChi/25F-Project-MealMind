from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import db

analytics_bp = Blueprint("analytics_bp", __name__)


# --------------- System Metrics & Alerts --------------------


@analytics_bp.route("/system-metrics", methods=["GET"])
def get_system_metrics():
    """
    List all system metrics with their latest snapshot (if any).
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT sm.MetricID,
                   sm.Name,
                   sm.Description,
                   ms.MeasuredAt AS LastMeasuredAt,
                   ms.Value AS LastValue
            FROM SystemMetric sm
            LEFT JOIN MetricSnapshot ms
              ON sm.MetricID = ms.MetricID
             AND ms.MeasuredAt = (
                 SELECT MAX(ms2.MeasuredAt)
                 FROM MetricSnapshot ms2
                 WHERE ms2.MetricID = sm.MetricID
             )
            ORDER BY sm.MetricID
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_system_metrics: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/system-metrics/<int:metric_id>/snapshots", methods=["GET"])
def get_metric_snapshots(metric_id: int):
    """
    Get time series snapshots for a metric.
    Query params: start (YYYY-MM-DD), end (YYYY-MM-DD)
    """
    try:
        start = request.args.get("start")
        end = request.args.get("end")

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT SnapshotID, MetricID, MeasuredAt, Value
            FROM MetricSnapshot
            WHERE MetricID = %s
        """
        params = [metric_id]
        if start:
            query += " AND MeasuredAt >= %s"
            params.append(start) # type: ignore
        if end:
            query += " AND MeasuredAt <= %s"
            params.append(end) # type: ignore

        query += " ORDER BY MeasuredAt"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_metric_snapshots: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/system-alerts", methods=["GET"])
def get_system_alerts():
    """
    List system alerts with optional filters.
    Query params: status, severity
    """
    try:
        status = request.args.get("status")
        severity = request.args.get("severity")

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT AlertID, MetricID, AlertType, Severity,
                   Message, CreatedAt, ResolvedAt, Status
            FROM SystemAlert
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND Status = %s"
            params.append(status)
        if severity:
            query += " AND Severity = %s"
            params.append(severity)

        query += " ORDER BY CreatedAt DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_system_alerts: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/system-alerts", methods=["POST"])
def create_system_alert():
    """
    Create a new system alert.
    Body JSON: {metric_id, alert_type, severity, message, status?}
    """
    try:
        data = request.get_json() or {}
        required = ["metric_id", "alert_type", "severity", "message"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        metric_id = data["metric_id"]
        alert_type = data["alert_type"]
        severity = data["severity"]
        message = data["message"]
        status = data.get("status", "open")

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        # Generate next AlertID
        cursor.execute("SELECT COALESCE(MAX(AlertID), 0) + 1 AS next_id FROM SystemAlert")
        next_id_row = cursor.fetchone()
        alert_id = next_id_row["next_id"] if isinstance(next_id_row, dict) else next_id_row[0]

        cursor.execute(
            """
            INSERT INTO SystemAlert
                (AlertID, MetricID, AlertType, Severity,
                 Message, CreatedAt, Status)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            """,
            (alert_id, metric_id, alert_type, severity, message, status),
        )
        conn.commit() # type: ignore
        cursor.close()
        return jsonify({"message": "System alert created", "alert_id": alert_id}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_system_alert: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/system-alerts/<int:alert_id>", methods=["GET"])
def get_system_alert(alert_id: int):
    """
    Get details for a single system alert.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        cursor.execute(
            """
            SELECT AlertID, MetricID, AlertType, Severity,
                   Message, CreatedAt, ResolvedAt, Status
            FROM SystemAlert
            WHERE AlertID = %s
            """,
            (alert_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return jsonify({"error": "Alert not found"}), 404
        return jsonify(row), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_system_alert: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/system-alerts/<int:alert_id>", methods=["PUT"])
def update_system_alert(alert_id: int):
    """
    Update fields on a system alert, e.g., mark as resolved.
    Body JSON: any of {metric_id, alert_type, severity, message, status, resolved_at}
    If status is set to a 'resolved' value and resolved_at is not provided,
    this will automatically set ResolvedAt = NOW().
    """
    try:
        data = request.get_json() or {}

        updates = []
        params = []

        field_map = {
            "metric_id": "MetricID",
            "alert_type": "AlertType",
            "severity": "Severity",
            "message": "Message",
            "status": "Status",
            "resolved_at": "ResolvedAt",
        }

        for key, column in field_map.items():
            if key in data:
                updates.append(f"{column} = %s")
                params.append(data[key])

        # Auto-set ResolvedAt if status is moving to resolved
        if "status" in data and data.get("resolved_at") is None:
            if data["status"].lower() in {"resolved", "closed"}:
                updates.append("ResolvedAt = NOW()")

        if not updates:
            return jsonify({"error": "No updatable fields provided"}), 400

        params.append(alert_id)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = f"""
            UPDATE SystemAlert
            SET {', '.join(updates)}
            WHERE AlertID = %s
        """
        cursor.execute(query, tuple(params))
        conn.commit() # type: ignore
        affected = cursor.rowcount
        cursor.close()

        if affected == 0:
            return jsonify({"error": "Alert not found"}), 404

        return jsonify({"message": "System alert updated"}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_system_alert: {e}")
        return jsonify({"error": str(e)}), 500


# --------------- Data Quality & Analytics --------------------


@analytics_bp.route("/data-quality-reports", methods=["GET"])
def get_data_quality_report():
    """
    Return a simple data quality report with some aggregate checks.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        report = {}

        # Orphan inventory items (should be 0 because of FK)
        cursor.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM InventoryItem ii
            LEFT JOIN Ingredient i ON ii.IngredientID = i.IngredientID
            WHERE i.IngredientID IS NULL
            """
        )
        orphan_inventory = cursor.fetchone()
        report["orphan_inventory_items"] = orphan_inventory["cnt"]

        # Recipes without ingredients
        cursor.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM Recipe r
            LEFT JOIN RecipeIngredient ri ON r.RecipeId = ri.RecipeID
            WHERE ri.RecipeID IS NULL
            """
        )
        recipes_without_ingredients = cursor.fetchone()
        report["recipes_without_ingredients"] = recipes_without_ingredients["cnt"]

        # Ingredients never used in recipes
        cursor.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM Ingredient i
            LEFT JOIN RecipeIngredient ri ON i.IngredientID = ri.IngredientID
            WHERE ri.IngredientID IS NULL
            """
        )
        unused_ingredients = cursor.fetchone()
        report["unused_ingredients"] = unused_ingredients["cnt"]

        cursor.close()
        return jsonify(report), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_data_quality_report: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/waste-statistics", methods=["GET"])
def get_waste_statistics():
    """
    Aggregated food waste statistics.
    Query params: period_id (optional), segment_id (optional)
    """
    try:
        period_id = request.args.get("period_id", type=int)
        segment_id = request.args.get("segment_id", type=int)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT ws.IngredientID,
                   i.CategoryID,
                   c.CategoryName,
                   SUM(ws.WastedAmount) AS TotalWastedAmount,
                   AVG(ws.WasteRatePercent) AS AvgWasteRatePercent
            FROM WasteStatistic ws
            LEFT JOIN Ingredient i ON ws.IngredientID = i.IngredientID
            LEFT JOIN Category c ON i.CategoryID = c.CategoryID
            WHERE 1=1
        """
        params = []
        if period_id:
            query += " AND ws.PeriodID = %s"
            params.append(period_id)
        if segment_id:
            query += " AND ws.SegmentID = %s"
            params.append(segment_id)

        query += """
            GROUP BY ws.IngredientID, i.CategoryID, c.CategoryName
            ORDER BY TotalWastedAmount DESC
        """
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_waste_statistics: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/recipe-usage-statistics", methods=["GET"])
def get_recipe_usage_statistics():
    """
    Aggregated recipe usage statistics.
    Query params: period_id (optional), segment_id (optional)
    """
    try:
        period_id = request.args.get("period_id", type=int)
        segment_id = request.args.get("segment_id", type=int)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        query = """
            SELECT rus.RecipeID,
                   r.Name,
                   SUM(rus.UsageCount) AS TotalUsageCount,
                   SUM(rus.UniqueUsers) AS TotalUniqueUsers
            FROM RecipeUsageStatistic rus
            JOIN Recipe r ON rus.RecipeID = r.RecipeId
            WHERE 1=1
        """
        params = []
        if period_id:
            query += " AND rus.PeriodID = %s"
            params.append(period_id)
        if segment_id:
            query += " AND rus.SegmentID = %s"
            params.append(segment_id)

        query += """
            GROUP BY rus.RecipeID, r.Name
            ORDER BY TotalUsageCount DESC
        """
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_recipe_usage_statistics: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/demographic-segments", methods=["GET"])
def get_demographic_segments():
    """
    Get all demographic segments.
    """
    try:
        conn = db.get_db()
        cursor = conn.cursor() # type: ignore
        cursor.execute(
            """
            SELECT SegmentID, Name, AgeMin, AgeMax, Region
            FROM DemographicSegment
            ORDER BY SegmentID
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return jsonify(rows), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_demographic_segments: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/analytics/reports", methods=["GET"])
def get_analytics_report():
    """
    High-level analytics summary combining waste and usage for a time period.
    Query params: period_id (optional)
    """
    try:
        period_id = request.args.get("period_id", type=int)

        conn = db.get_db()
        cursor = conn.cursor() # type: ignore

        # Total waste for the period
        waste_query = """
            SELECT SUM(WastedAmount) AS TotalWaste
            FROM WasteStatistic
            WHERE 1=1
        """
        params = []
        if period_id:
            waste_query += " AND PeriodID = %s"
            params.append(period_id)

        cursor.execute(waste_query, tuple(params))
        waste_row = cursor.fetchone()
        total_waste = waste_row["TotalWaste"]

        # Total recipe usage for the period
        usage_query = """
            SELECT SUM(UsageCount) AS TotalUsage,
                   SUM(UniqueUsers) AS TotalUniqueUsers
            FROM RecipeUsageStatistic
            WHERE 1=1
        """
        params = []
        if period_id:
            usage_query += " AND PeriodID = %s"
            params.append(period_id)

        cursor.execute(usage_query, tuple(params))
        usage_row = cursor.fetchone()
        total_usage = usage_row["TotalUsage"]
        total_unique_users = usage_row["TotalUniqueUsers"]

        cursor.close()

        report = {
            "period_id": period_id,
            "total_waste": total_waste,
            "total_recipe_usage": total_usage,
            "total_unique_users": total_unique_users,
        }

        return jsonify(report), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_analytics_report: {e}")
        return jsonify({"error": str(e)}), 500
