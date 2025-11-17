import os
import pathlib
from typing import Optional

import models
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo

DIR = pathlib.Path(__file__).parent

load_dotenv(DIR / ".env", override=True)
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")

mongo = PyMongo(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[models.User]:
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        return None
    return models.User(user_data)


if __name__ == "__main__":
    app.run(debug=True)
