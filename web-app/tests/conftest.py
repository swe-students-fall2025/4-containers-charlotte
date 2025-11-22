"""Mocks client, db, and user"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from bson import ObjectId

from app import create_app


@pytest.fixture
def _app():
    """Create and configure a new app instance for testing."""
    _app = create_app()
    _app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test_secret_key",
            "LOGIN_DISABLED": True,
        }
    )
    return _app


@pytest.fixture
def client(_app):
    """Client for testing."""
    return _app.test_client()


@pytest.fixture
def runner(_app):
    """A CLI runner for the app."""
    return _app.test_cli_runner()


@pytest.fixture
def mock_db_auth():
    """Mocks DB for app/auth.py"""
    with patch("app.auth.db") as db_mock:
        db_mock.users.find_one = MagicMock(return_value=None)
        db_mock.users.insert_one = MagicMock()
        db_mock.users.find_one_and_update = MagicMock()
        db_mock.history.insert_one = MagicMock()

        yield db_mock


@pytest.fixture
def mock_db():
    """Mocks DB for app/db.py"""
    with patch("app.db") as db_mock:
        db_mock.users.find_one = MagicMock(return_value=None)
        db_mock.users.insert_one = MagicMock()
        db_mock.users.find_one_and_update = MagicMock()
        db_mock.history.insert_one = MagicMock()
        db_mock.history.find_one = MagicMock(
            return_value={
                "_id": ObjectId(),
                "owner": ObjectId(),
                "timestamp": datetime.fromisoformat("2025-01-01T12:00:00"),
                "source_language": "fr",
                "english_text": "Hello",
                "processing_time": 1.23,
                "output_file_id": ObjectId(),
            }
        )
        db_mock.history.find = MagicMock(return_value=[])

        yield db_mock


@pytest.fixture
def mock_user():
    """Mock the User class."""
    with patch("app.auth.models.User") as user_mock:
        mock_user_instance = user_mock.return_value
        mock_user_instance.set_password.return_value = None
        valid_id = str(ObjectId())
        mock_user_instance.id = valid_id
        mock_user_instance.get_id.return_value = valid_id

        yield user_mock


@pytest.fixture
def mock_ml_client_response():
    """Mock the ML client's response to requests.post"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "timestamp": "2025-01-01T12:00:00",
        "source_language": "fr",
        "english_text": "Hello",
        "processing_time": 1.23,
        "output_file_id": str(ObjectId()),
    }
    return mock_response
