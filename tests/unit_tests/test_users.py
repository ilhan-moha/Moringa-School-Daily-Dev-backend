from models.user import User

def test_password_is_hashed():
    user = User(
        first_name="John",
        last_name="Doe",
        email="john@example.com"
    )
    user.set_password("password123")
    assert user.password_hash != "password123"
    assert user.check_password("password123")

def test_wrong_password_fails():
    user = User(
        first_name="John",
        last_name="Doe",
        email="john@example.com"
    )
    user.set_password("password123")
    assert not user.check_password("wrongpassword")