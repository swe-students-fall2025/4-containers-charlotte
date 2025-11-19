"""Flask App"""

import os
import pathlib
from typing import Optional

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, url_for
from flask_login import LoginManager, current_user, login_required

import models
from auth import auth_bp
from db import db

DIR = pathlib.Path(__file__).parent

# Load environment variables
load_dotenv(DIR / ".env", override=True)

app = Flask(__name__, template_folder="./templates")
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

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth.login"))


@app.route("/upload")
def upload_page():
    """Render the audio upload page."""
    return render_template("upload.html")


@app.route("/result")
@login_required
def result_page():
    """Render the result page which loads data via JS."""
    return render_template("result.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page for a user"""

    return render_template("dashboard.html")


@app.route("/history")
@login_required
def history():
    """History of uses by current user"""

    return render_template("history.html")


if __name__ == "__main__":
    app.run(debug=True)
