# tests/test_models_user.py

from bson import ObjectId

from models import User


def test_user_set_and_check_password():
    """
    User.set_password should hash the password,
    and check_password should validate it correctly.
    """
    user_data = {
        "_id": ObjectId(),
        "username": "testuser",
        "password_hash": "",
        "history": [],
    }

    user = User(user_data)

    user.set_password("supersecret")

    # Password should not be stored in plaintext
    assert user.password_hash != "supersecret"
    assert user.data["password_hash"] == user.password_hash

    # Check correct password
    assert user.check_password("supersecret") is True
    # Check incorrect password
    assert user.check_password("wrong") is False


def test_user_to_dict_excludes_id():
    """
    User.to_dict() should not include the '_id' field and should
    include username, password_hash, history.
    """
    user_data = {
        "_id": ObjectId(),
        "username": "testuser",
        "password_hash": "hash",
        "history": ["entry1"],
    }

    user = User(user_data)
    d = user.to_dict()

    assert "_id" not in d
    assert d["username"] == "testuser"
    assert d["password_hash"] == "hash"
    assert d["history"] == ["entry1"]
