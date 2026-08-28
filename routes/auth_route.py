from flask import Blueprint, request, jsonify
from flask_jwt_extended import (create_access_token, get_jwt_identity, jwt_required)
from services.auth_service import register_user, authenticate_user
from models.user import User
from extensions import db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/signup")
def signup():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400
    
    required_fields = ["first_name", "last_name", "email", "password"]
    missing_fields = [
        field for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({"message": "Missing required fields", "fields": missing_fields}), 400
    try:
        user = register_user(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"]
        )

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role
            }
        }), 201

    except ValueError as error:
        return jsonify({
            "message": str(error)
        }), 409

@auth_bp.post("/login")
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = authenticate_user(email, password)

    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.get("/me")
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
    }), 200