"""Flask App"""

import os
import pathlib
from typing import Optional

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import LoginManager

import models
from auth import auth_bp
from db import db

DIR = pathlib.Path(__file__).parent

# Load environment variables
load_dotenv(DIR / ".env", override=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[models.User]:
    """Load currently logged-in user data"""

    user_data = db.users.find_one({"_id": ObjectId(user_id)})

    if not user_data:
        return None

    return models.User(user_data)


# Register auth blueprint
app.register_blueprint(auth_bp)


@app.route("/")
def index():
    """Landing page"""
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    """Render the audio upload page."""
    return render_template("upload.html")


@app.route("/history")
def history_page():
    """Render the history page showing past results."""
    return render_template("history.html")


@app.route("/result")
def result_page():
    """Render the result page which loads data via JS."""
    return render_template("result.html")


if __name__ == "__main__":
    app.run(debug=True)
