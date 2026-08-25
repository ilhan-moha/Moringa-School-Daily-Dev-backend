from app import app

def test_signup():
    client = app.test_client()
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "newtestauth@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201

def test_login():
    client = app.test_client()
    response = client.post(
        "/api/auth/login",
        json={
            "email": "jane@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Login successful"
    assert "access_token" in data
    assert data["user"]["email"] == "jane@example.com"

def test_get_current_user():
    client = app.test_client()
    # Login first to get JWT
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "jane@example.com",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200
    login_data = login_response.get_json()
    access_token = login_data["access_token"]
    # Use JWT to access /me
    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "user" in data
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["first_name"] == "Jane"
    assert data["user"]["last_name"] == "Doe"
