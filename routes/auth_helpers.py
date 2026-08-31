from flask_jwt_extended import get_jwt_identity
from extensions import db
from models.user import User


def get_current_user():
    user_id = get_jwt_identity()

    if not user_id:
        return None

    return db.session.get(User, int(user_id))