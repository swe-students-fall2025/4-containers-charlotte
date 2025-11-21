"""Flask App"""

import os
import pathlib
from typing import Optional

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required
import requests

import models
from auth import auth_bp
from db import db

DIR = pathlib.Path(__file__).parent
CLIENT_URL = "127.0.0.1:5001"  # change based on docker config

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


@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload_page():
    """Render the audio upload page."""

    if request.method == "POST":
        url = f"{CLIENT_URL}/api/process"
        audio_file = request.files["audio"]

        if audio_file.mimetype not in [
            "audio/mpeg",
            "audio/mp4",
            "audio/wav",
            "audio/flac",
            "audio/ogg",
        ]:
            flash(
                "Only the following file formats are accepted: .mp3, .m4a, .wav, .ogg, .flac",
                "danger"
            )
            return render_template("upload.html")

        if audio_file.filename == "":
            flash("No selected file", "danger")
            return render_template("upload.html")

        files = {
            "audio": (audio_file.filename, audio_file.stream, audio_file.mimetype)
        }

        res = requests.post(url, files=files)
        if res.status_code != 200:
            json = res.json()
            flash(f"{res.status_code} error: {json['error']}", "danger")
            return render_template("upload.html")

    return render_template("upload.html")


@app.route("/result/{result_id}")
@login_required
def result_page(result_id: str):
    """Render a result page"""

    res = db.history.find_one({"_id": ObjectId(result_id)})

    if not res:
        flash("Audio translation not found", "danger")
        return redirect("dashboard")

    return render_template("result.html", result=res)


@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page for a user"""

    return render_template("dashboard.html")


@app.route("/history")
@login_required
def get_history():
    """History of uses by current user"""

    user: dict = db.users.find_one({"_id": ObjectId(current_user.id)})
    result_history = db.history.find(
        {"$or": [{"_id": result_id for result_id in user["history"]}]}
    )

    return render_template("history.html", history=list(result_history))


if __name__ == "__main__":
    app.run(debug=True)
