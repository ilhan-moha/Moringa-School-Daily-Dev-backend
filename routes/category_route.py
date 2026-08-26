from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.category import Category
from routes.auth_helpers import get_current_user

category_bp = Blueprint("category", __name__, url_prefix="/api/categories")


@category_bp.route("", methods=["GET"])
def list_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories]), 200


@category_bp.route("", methods=["POST"])
@jwt_required()
def create_category():
    current_user = get_current_user()
    if current_user.role not in ("admin", "writer"):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category already exists"}), 409

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


@category_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    current_user = get_current_user()
    if current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 200