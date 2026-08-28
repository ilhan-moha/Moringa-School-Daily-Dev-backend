from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.comment import Comment
from routes.auth_helpers import get_current_user

comment_bp = Blueprint("comment", __name__, url_prefix="/api/comments")


@comment_bp.route("/content/<int:content_id>", methods=["GET"])
def get_thread(content_id):
    top_level = (
        Comment.query.filter_by(content_id=content_id, parent_comment_id=None)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return jsonify([c.to_dict() for c in top_level]), 200


@comment_bp.route("", methods=["POST"])
@jwt_required()
def create_comment():
    current_user = get_current_user()
    data = request.get_json() or {}
    if not data.get("content_id") or not data.get("text"):
        return jsonify({"error": "content_id and text are required"}), 400

    comment = Comment(
        content_id=data["content_id"],
        user_id=current_user.id,
        parent_comment_id=data.get("parent_comment_id"),
        text=data["text"],
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201


@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    current_user = get_current_user()
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted"}), 200