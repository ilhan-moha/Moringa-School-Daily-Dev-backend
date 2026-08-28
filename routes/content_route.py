from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.content import Content
from services import content_service
from services.recommendation_service import get_recommended_content
from routes.auth_helpers import get_current_user

content_bp = Blueprint("content", __name__, url_prefix="/api/content")


@content_bp.route("", methods=["GET"])
def list_content():
    category_id = request.args.get("category_id", type=int)
    items = content_service.get_feed(category_id=category_id)
    return jsonify(items), 200


@content_bp.route("/recommended", methods=["GET"])
@jwt_required()
def recommended():
    current_user = get_current_user()
    items = get_recommended_content(current_user)
    return jsonify(items), 200


@content_bp.route("/pending", methods=["GET"])
@jwt_required()
def pending_review():
    current_user = get_current_user()
    if current_user.role not in ("admin", "writer"):
        return jsonify({"error": "Forbidden"}), 403
    items = content_service.get_pending()
    return jsonify(items), 200


@content_bp.route("/<int:content_id>", methods=["GET"])
def get_content(content_id):
    item = Content.query.get_or_404(content_id)
    return jsonify(content_service.get_content_with_counts(item)), 200


@content_bp.route("", methods=["POST"])
@jwt_required()
def create_content():
    current_user = get_current_user()
    data = request.get_json() or {}
    error = content_service.validate_content_payload(data)
    if error:
        return jsonify({"error": error}), 400

    item = content_service.create_content(data, current_user)
    return jsonify(item.to_dict()), 201


@content_bp.route("/<int:content_id>", methods=["PATCH"])
@jwt_required()
def update_content(content_id):
    current_user = get_current_user()
    item = Content.query.get_or_404(content_id)
    if item.author_id != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json() or {}
    item = content_service.update_content(item, data)
    return jsonify(item.to_dict()), 200


@content_bp.route("/<int:content_id>/approve", methods=["POST"])
@jwt_required()
def approve(content_id):
    current_user = get_current_user()
    if current_user.role not in ("admin", "writer"):
        return jsonify({"error": "Forbidden"}), 403

    item = Content.query.get_or_404(content_id)
    item = content_service.approve_content(item)
    return jsonify(item.to_dict()), 200


@content_bp.route("/<int:content_id>", methods=["DELETE"])
@jwt_required()
def delete_content(content_id):
    current_user = get_current_user()
    if current_user.role not in ("admin", "writer"):
        return jsonify({"error": "Forbidden"}), 403

    item = Content.query.get_or_404(content_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Content removed"}), 200