from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.user import User
from routes.auth_helpers import get_current_user

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/users", methods=["POST"])
@jwt_required()
def create_user():
    current_user = get_current_user()
    if current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}

    required_fields = ["first_name", "last_name", "email", "password"]
    missing_fields = [
        field for field in required_fields
        if not data.get(field)]

    if missing_fields:
        return jsonify({"error": "Missing required fields", "fields": missing_fields}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email is already registered"}), 409

    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        password=data["password"],
        role=data.get("role", "user")
    )

    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User has been created successfully", "user": user.to_dict()}), 201

@admin_bp.route("/users/<int:user_id>/deactivate", methods=["PATCH"])
@jwt_required()
def deactivate_user(user_id):
    current_user = get_current_user()

    if current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    user = User.query.get_or_404(user_id)

    if not user.is_active:
        return jsonify({"message": "User is already deactivated"}), 400

    user.is_active = False
    db.session.commit()

    return jsonify({"message": "User has been deactivated successfully"}), 200