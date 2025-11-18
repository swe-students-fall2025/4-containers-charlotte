"""User and data models"""

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    """User model wrapper"""

    def __init__(self, user_data: dict):
        # Store the original dictionary (important for DB operations)
        self.data = user_data

        self.id = str(user_data.get("_id", ""))
        self.username = user_data.get("username", "")
        self.password_hash = user_data.get("password_hash", "")
        self.history = user_data.get("history", [])

    def set_password(self, password: str):
        """Hash password and update both object + underlying dict"""
        hashed = generate_password_hash(password)
        self.password_hash = hashed
        self.data["password_hash"] = hashed

    def check_password(self, password: str) -> bool:
        """Check the password provided against the stored password"""
        return check_password_hash(self.password_hash, password)
