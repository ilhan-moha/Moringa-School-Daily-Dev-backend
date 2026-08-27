from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.profile import Profile
from models.user import User

profile_bp = Blueprint(
    "profile",
    __name__,
    url_prefix="/api/profile"
)

@profile_bp.get("/me")
@jwt_required()
def get_my_profile():
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=int(user_id)).first()
    if not profile:
        return jsonify({"message": "Profile not found"}), 404
    return jsonify({
        "profile": profile.to_dict()
    }), 200

@profile_bp.post("/me")
@jwt_required()
def create_my_profile():
    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({"message": "User not found"}), 404

    existing_profile = Profile.query.filter_by(user_id=int(user_id)).first()

    if existing_profile:
        return jsonify({"message": "Profile already exists"}), 409

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    profile = Profile(
        user_id=int(user_id),
        bio=data.get("bio"),
        avatar_url=data.get("avatar_url"),
        github_url=data.get("github_url"),
        linkedin_url=data.get("linkedin_url"),
        website_url=data.get("website_url")
    )

    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Profile has been created successfully", "profile": profile.to_dict()}), 201

@profile_bp.put("/me")
@jwt_required()
def update_my_profile():
    user_id = get_jwt_identity()

    profile = Profile.query.filter_by(user_id=int(user_id)).first()

    if not profile:
        return jsonify({"message": "Profile not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is required"}), 400

    if "bio" in data:
        profile.bio = data["bio"]
    if "avatar_url" in data:
        profile.avatar_url = data["avatar_url"]
    if "github_url" in data:
        profile.github_url = data["github_url"]
    if "linkedin_url" in data:
        profile.linkedin_url = data["linkedin_url"]
    if "website_url" in data:
        profile.website_url = data["website_url"]

    db.session.commit()

    return jsonify({"message": "Profile has been updated successfully", "profile": profile.to_dict()}), 200

@profile_bp.get("/<int:user_id>")
@jwt_required()
def get_user_profile(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    profile = Profile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({"message": "Profile not found"}), 404

    return jsonify({"profile": profile.to_dict()}), 200
