from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.reaction import Reaction
from routes.auth_helpers import get_current_user

reaction_bp = Blueprint("reaction", __name__, url_prefix="/api/reactions")


@reaction_bp.route("/content/<int:content_id>", methods=["POST"])
@jwt_required()
def react(content_id):
    current_user = get_current_user()
    data = request.get_json() or {}
    reaction_type = data.get("type")
    if reaction_type not in ("like", "dislike"):
        return jsonify({"error": "type must be like or dislike"}), 400

    existing = Reaction.query.filter_by(content_id=content_id, user_id=current_user.id).first()
    if existing:
        existing.type = reaction_type
    else:
        db.session.add(Reaction(content_id=content_id, user_id=current_user.id, type=reaction_type))
    db.session.commit()

    likes = Reaction.query.filter_by(content_id=content_id, type="like").count()
    dislikes = Reaction.query.filter_by(content_id=content_id, type="dislike").count()
    return jsonify({"likes": likes, "dislikes": dislikes}), 200


@reaction_bp.route("/content/<int:content_id>", methods=["DELETE"])
@jwt_required()
def remove_reaction(content_id):
    current_user = get_current_user()
    existing = Reaction.query.filter_by(content_id=content_id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    return jsonify({"message": "Reaction removed"}), 200