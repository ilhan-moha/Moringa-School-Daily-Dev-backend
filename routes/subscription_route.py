from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.subscription import Subscription
from models.category import Category
from routes.auth_helpers import get_current_user

subscription_bp = Blueprint("subscription", __name__, url_prefix="/api/subscriptions")


@subscription_bp.route("", methods=["GET"])
@jwt_required()
def my_subscriptions():
    current_user = get_current_user()
    subs = Subscription.query.filter_by(user_id=current_user.id).all()
    category_ids = [s.category_id for s in subs]
    categories = Category.query.filter(Category.id.in_(category_ids)).all()
    return jsonify([c.to_dict() for c in categories]), 200


@subscription_bp.route("/<int:category_id>", methods=["POST"])
@jwt_required()
def subscribe(category_id):
    current_user = get_current_user()
    Category.query.get_or_404(category_id)
    existing = Subscription.query.filter_by(
        user_id=current_user.id, category_id=category_id
    ).first()
    if existing:
        return jsonify({"message": "Already subscribed"}), 200

    db.session.add(Subscription(user_id=current_user.id, category_id=category_id))
    db.session.commit()
    return jsonify({"message": "Subscribed"}), 201


@subscription_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
def unsubscribe(category_id):
    current_user = get_current_user()
    existing = Subscription.query.filter_by(
        user_id=current_user.id, category_id=category_id
    ).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    return jsonify({"message": "Unsubscribed"}), 200