from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.wishlist import Wishlist
from models.content import Content
from routes.auth_helpers import get_current_user

wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/api/wishlist")


@wishlist_bp.route("", methods=["GET"])
@jwt_required()
def my_wishlist():
    current_user = get_current_user()
    entries = Wishlist.query.filter_by(user_id=current_user.id).all()
    content_ids = [e.content_id for e in entries]
    items = Content.query.filter(Content.id.in_(content_ids)).all()
    return jsonify([c.to_dict() for c in items]), 200


@wishlist_bp.route("/<int:content_id>", methods=["POST"])
@jwt_required()
def add_to_wishlist(content_id):
    current_user = get_current_user()
    Content.query.get_or_404(content_id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, content_id=content_id).first()
    if not existing:
        db.session.add(Wishlist(user_id=current_user.id, content_id=content_id))
        db.session.commit()
    return jsonify({"message": "Added to wishlist"}), 201


@wishlist_bp.route("/<int:content_id>", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist(content_id):
    current_user = get_current_user()
    existing = Wishlist.query.filter_by(user_id=current_user.id, content_id=content_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    return jsonify({"message": "Removed from wishlist"}), 200