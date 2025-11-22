"""Tests register"""

from unittest.mock import MagicMock


def test_register_get(client):
    """Test GET /register renders the page."""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Sign Up" in response.data


def test_register_post_success(client, mock_db_auth, mock_user):
    """Test POST /register with valid data creates a user and redirects."""
    mock_db_auth.users.find_one.return_value = None
    mock_insert = MagicMock()
    mock_insert.inserted_id = "fake_id"
    mock_db_auth.users.insert_one.return_value = mock_insert

    mock_user_instance = mock_user.return_value
    mock_user_instance.to_dict.return_value = {"username": "test"}

    response = client.post(
        "/register",
        data={
            "username": "test",
            "password": "password",
            "confirmPassword": "password",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_register_post_existing_username(client, mock_db_auth):
    """Test POST /register fails when username exists."""
    mock_db_auth.users.find_one.return_value = {"username": "test"}

    response = client.post(
        "/register",
        data={
            "username": "test",
            "password": "password",
            "confirmPassword": "password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Username already exists" in response.data


def test_register_post_password_mismatch(client, mock_db_auth):
    """Test POST /register fails when passwords do not match."""
    mock_db_auth.users.find_one.return_value = None

    response = client.post(
        "/register",
        data={
            "username": "test",
            "password": "password1",
            "confirmPassword": "password2",
        },
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data
