from models.user import User
from extensions import db

def register_user(first_name, last_name, email, password):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("Email already registered")
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        role="user"
    )

    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return user