"""Mocks client, db, and user"""

from unittest.mock import MagicMock, patch
import pytest
from bson import ObjectId
from app import create_app


@pytest.fixture
def _app():
    """Create and configure a new app instance for testing."""
    _app = create_app()
    _app.config.update(
        {"TESTING": True, "WTF_CSRF_ENABLED": False, "SECRET_KEY": "test_secret_key"}
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
def mock_db():
    """Mock database for testing."""
    with patch("app.auth.db") as db_mock:
        db_mock.users.find_one = MagicMock(return_value=None)
        db_mock.users.insert_one = MagicMock()
        db_mock.users.find_one_and_update = MagicMock()
        db_mock.history.insert_one = MagicMock()
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
