"""Classes used throughout the assignment"""

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    """Class for users"""

    def __init__(self, user_data: dict):
        self.id: str = str(user_data.get("_id", ""))
        self.username: str = user_data.get("username", "")
        self.password_hash: str = user_data.get("password_hash", "")
        self.history: list = user_data.get("history", [])

    def to_dict(self) -> dict:
        """Return a dictionary representation of User class without _id"""

        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "history": self.history,
        }

    def set_password(self, password: str) -> str:
        """Set the password for a user"""

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check the password provided against the user's stored password"""

        return check_password_hash(self.password_hash, password)
