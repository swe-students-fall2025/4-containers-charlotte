"""Flask app"""

import os
import pathlib
from typing import Optional

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

import models
from db import get_history_collection  # unified DB helper

DIR = pathlib.Path(__file__).parent

# Load environment variables
load_dotenv(DIR / ".env", override=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Initialize login manager
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[models.User]:
    """Load currently logged-in user data"""
    history_collection = get_history_collection()
    user_data = history_collection.database.users.find_one({"_id": ObjectId(user_id)})

    if not user_data:
        return None

    return models.User(user_data)


@app.route("/")
def index():
    return "Web App Running"


if __name__ == "__main__":
    app.run(debug=True)
