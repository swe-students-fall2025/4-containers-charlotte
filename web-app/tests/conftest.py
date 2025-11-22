import pytest
from unittest.mock import MagicMock, patch
from app import create_app
from app.models import User
from bson import ObjectId


@pytest.fixture
def app():
    """Create and configure a new app instance for testing."""
    app = create_app()
    app.config.update(
        {"TESTING": True, "WTF_CSRF_ENABLED": False, "SECRET_KEY": "test_secret_key"}
    )
    return app


@pytest.fixture
def client(app):
    """Client for testing."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def mock_db():
    """Mock database for testing."""
    with patch("app.auth.db") as mock_db:
        mock_db.users.find_one = MagicMock(return_value=None)
        mock_db.users.insert_one = MagicMock()
        mock_db.users.find_one_and_update = MagicMock()
        mock_db.history.insert_one = MagicMock()
        mock_db.history.find = MagicMock(return_value=[])
        yield mock_db


@pytest.fixture
def mock_user():
    """Mock the User class."""
    with patch("app.auth.models.User") as MockUser:
        mock_user_instance = MockUser.return_value
        mock_user_instance.to_dict.return_value = {"username": "test"}
        mock_user_instance.set_password.return_value = None
        valid_id = str(ObjectId())
        mock_user_instance.id = valid_id
        mock_user_instance.get_id.return_value = valid_id

        yield MockUser
