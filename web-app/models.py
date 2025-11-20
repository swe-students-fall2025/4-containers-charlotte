"""User and data models"""

from bson import ObjectId
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    """User model wrapper"""

    def __init__(self, user_data: dict):
        self.id: str = str(user_data.get("_id", ""))
        self.username: str = user_data.get("username", "")
        self.password_hash: str = user_data.get("password_hash", "")
        self.history: list[ObjectId] = user_data.get("history", [])

    def to_dict(self):
        """Get dictionary representation of the user"""

        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "history": self.history,
        }

    def set_password(self, password: str):
        """Hash password and update both object + underlying dict"""
        hashed = generate_password_hash(password)
        self.password_hash = hashed

    def check_password(self, password: str) -> bool:
        """Check the password provided against the stored password"""
        return check_password_hash(self.password_hash, password)
