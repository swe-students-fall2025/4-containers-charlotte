# tests/test_auth_extra.py
"""
Extra auth tests: login edge cases.
"""

import pytest

# IMPORTANT:
# Replace "test_app" below with the actual filename of your current test file
# that defines the fixtures: _app, client, mock_db_auth, mock_user
from test_app import client, mock_db_auth, mock_user  # noqa: F401


def test_login_unknown_user(client, mock_db_auth, mock_user):
    """
    POST /login with a username that does not exist in the DB
    should not crash and should show a login error message.
    """
    # DB returns no user
    mock_db_auth.users.find_one.return_value = None

    response = client.post(
        "/login",
        data={"username": "ghost", "password": "whatever"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    # You already assert this message in your existing failure test,
    # so we safely reuse the same string.
    assert b"Login unsuccessful. Please check username and password." in response.data


def test_login_missing_password(client, mock_db_auth, mock_user):
    """
    POST /login with missing password should stay on login page
    and not redirect to /dashboard.
    """
    # Mock a user existing in DB so handler reaches form validation
    mock_db_auth.users.find_one.return_value = {
        "_id": "1234",
        "username": "test",
        "password_hash": "hashed",
    }

    response = client.post(
        "/login",
        data={"username": "test"},  # no password field
        follow_redirects=True,
    )

    # Should not redirect to dashboard (no 302 to /dashboard)
    assert response.status_code == 200
    assert b"Login" in response.data
