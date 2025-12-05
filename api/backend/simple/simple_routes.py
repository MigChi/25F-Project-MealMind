from flask import Blueprint, jsonify, make_response, current_app

simple_routes = Blueprint("simple_routes", __name__)

@simple_routes.route("/", methods=["GET"])
def welcome():
    current_app.logger.info("GET / handler")
    html = "<h1>Welcome to the MealMind REST API</h1>"
    response = make_response(html)
    response.status_code = 200
    return response

@simple_routes.route("/health", methods=["GET"])
def health():
    current_app.logger.info("GET /health handler")
    return jsonify({"status": "ok"}), 200
