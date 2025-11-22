"""Tests login"""

def test_login_get(client):
    """Test GET /login returns 200."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_post_successful(client, mock_db, mock_user):
    """Test POST /login returns 302 and redirects to dashboard"""
    mock_db.users.find_one.return_value = {"username": "test", "password": "hashed"}
    mock_user.return_value.check_password.return_value = True

    response = client.post(
        "/login",
        data={"username": "test", "password": "correct"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_login_post_failure(client, mock_db, mock_user):
    """Test POST /login with invalid credentials flashes error."""
    # Mock DB to return a user object (so we reach password check)
    mock_db.users.find_one.return_value = {
        "_id": "1234",
        "username": "test",
        "password_hash": "hashed",
    }

    # Mock the User instance to fail password check
    mock_user_instance = mock_user.return_value
    mock_user_instance.check_password.return_value = False

    response = client.post(
        "/login",
        data={"username": "test", "password": "wrongpassword"},
        follow_redirects=True,
    )

    assert b"Login unsuccessful. Please check username and password." in response.data
