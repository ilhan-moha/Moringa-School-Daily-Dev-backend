from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash


user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/api/users"
)

# HELPER

def get_logged_in_user():
    user_id = get_jwt_identity()

    if not user_id:
        return None

    return db.session.get(User, int(user_id))


def user_to_dict(user):
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
            if user.created_at else None,
        "updated_at": user.updated_at.isoformat()
            if user.updated_at else None,
    }

# GET CURRENT USER

@user_bp.get("/me")
@jwt_required()
def get_current_user():

    user = get_logged_in_user()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "user": user_to_dict(user)
    }), 200


# UPDATE CURRENT USER

@user_bp.put("/me")
@jwt_required()
def update_current_user():

    user = get_logged_in_user()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    data = request.get_json() or {}

    if "first_name" in data:
        user.first_name = data["first_name"].strip()

    if "last_name" in data:
        user.last_name = data["last_name"].strip()

    if "email" in data:
        email = data["email"].strip().lower()

        existing_user = User.query.filter(
            User.email == email,
            User.id != user.id
        ).first()

        if existing_user:
            return jsonify({
                "message": "Email has already been registered"
            }), 409

        user.email = email

    try:
        db.session.commit()

        return jsonify({
            "message": "User updated successfully",
            "user": user_to_dict(user)
        }), 200

    except Exception as error:
        db.session.rollback()

        print("UPDATE USER ERROR:", error)

        return jsonify({
            "message": "Failed to update user"
        }), 500

# DEACTIVATE CURRENT USER

@user_bp.delete("/me")
@jwt_required()
def deactivate_current_user():

    user = get_logged_in_user()

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    user.is_active = False

    db.session.commit()

    return jsonify({
        "message": "Account deactivated successfully"
    }), 200


# GET ALL USERS

@user_bp.get("")
@jwt_required()
def get_all_users():

    current_user = get_logged_in_user()

    if not current_user:
        return jsonify({
            "message": "User not found"
        }), 404

    if current_user.role != "admin":
        return jsonify({
            "message": "Forbidden. Admin access required."
        }), 403

    users = User.query.order_by(
        User.created_at.desc()
    ).all()

    return jsonify({
        "users": [
            user_to_dict(user)
            for user in users
        ]
    }), 200


# CREATE USER
# ADMIN ONLY

@user_bp.post("")
@jwt_required()
def create_user():

    current_user = get_logged_in_user()

    if not current_user:
        return jsonify({
            "message": "User not found"
        }), 404

    if current_user.role != "admin":
        return jsonify({
            "message": "Forbidden. Admin access required."
        }), 403

    data = request.get_json() or {}

    required_fields = [
        "first_name",
        "last_name",
        "email",
        "password",
        "role"
    ]

    missing_fields = [
        field
        for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            "message": "Missing required fields",
            "fields": missing_fields
        }), 400

    first_name = data["first_name"].strip()
    last_name = data["last_name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]
    role = data["role"].strip().lower()

    allowed_roles = [
        "user",
        "writer",
        "admin"
    ]

    if role not in allowed_roles:
        return jsonify({
            "message": "Invalid role"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email has already been registered"
        }), 409

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        is_active=True
    )

    try:
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User created successfully",
            "user": user_to_dict(new_user)
        }), 201

    except Exception as error:
        db.session.rollback()

        print("CREATE USER ERROR:", error)

        return jsonify({
            "message": "Failed to create user"
        }), 500



# UPDATE USER

@user_bp.patch("/<int:user_id>")
@jwt_required()
def update_user(user_id):

    current_user = get_logged_in_user()

    if not current_user:
        return jsonify({
            "message": "User not found"
        }), 404

    if current_user.role != "admin":
        return jsonify({
            "message": "Forbidden. Admin access required."
        }), 403

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    data = request.get_json() or {}

    # CHANGE ROLE
   
    if "role" in data:

        role = str(
            data["role"]
        ).strip().lower()

        allowed_roles = [
            "user",
            "writer",
            "admin"
        ]

        if role not in allowed_roles:
            return jsonify({
                "message": "Invalid role"
            }), 400

        user.role = role

    # ACTIVATE / DEACTIVATE
    
    if "is_active" in data:

        if not isinstance(
            data["is_active"],
            bool
        ):
            return jsonify({
                "message": "is_active must be true or false"
            }), 400

        user.is_active = data["is_active"]

    try:
        db.session.commit()

        return jsonify({
            "message": "User updated successfully",
            "user": user_to_dict(user)
        }), 200

    except Exception as error:
        db.session.rollback()

        print("ADMIN UPDATE USER ERROR:", error)

        return jsonify({
            "message": "Failed to update user"
        }), 500

# GET SINGLE USER

@user_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "user": user_to_dict(user)
    }), 200