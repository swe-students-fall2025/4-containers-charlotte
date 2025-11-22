"""Flask App"""

import os
import pathlib
from datetime import datetime
from io import BytesIO
from typing import Optional

import requests
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import LoginManager, current_user, login_required

from . import models
from .auth import auth_bp
from .db import db, gridfs

DIR = pathlib.Path(__file__).parent.parent
CLIENT_URL = "http://ml:5001"  # ML-client; change based on docker config


def create_app():
    """Create app to export"""
    # Load environment variables
    load_dotenv(DIR / ".env", override=True)

    # Configure app
    app = Flask(
        __name__, template_folder=DIR / "templates", static_folder=DIR / "static"
    )
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

        # Upload and send an audio file to ML client
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
                    "danger",
                )
                return render_template("upload.html")

            if audio_file.filename == "":
                flash("No selected file", "danger")
                return render_template("upload.html")

            files = {
                "audio": (audio_file.filename, audio_file.stream, audio_file.mimetype)
            }

            res = requests.post(url, files=files, timeout=60)
            json: dict = res.json()
            if res.status_code != 200:
                flash(
                    f"{res.status_code} error: {json.get("error", "Unknown error")}",
                    "danger",
                )
                return render_template("upload.html")

            # Save operation metadata into history collection
            timestamp = json.get("timestamp")
            history_entry = {
                "owner": ObjectId(current_user.id),
                "timestamp": datetime.fromisoformat(timestamp) if timestamp else None,
                "source_language": json.get("source_language"),
                "english_text": json.get("english_text"),
                "processing_time": json.get("processing_time"),
                "output_file_id": ObjectId(json.get("output_file_id")),
                "file_name": audio_file.filename,
            }

            # Add operation to history collection, and history of the user
            inserted = db.history.insert_one(history_entry)
            inserted_id = inserted.inserted_id
            db.users.find_one_and_update(
                {"_id": ObjectId(current_user.id)}, {"$push": {"history": inserted_id}}
            )

            return redirect(url_for("result_page", result_id=str(inserted_id)))

        return render_template("upload.html")

    @app.route("/result/<result_id>")
    @login_required
    def result_page(result_id: str):
        """Render a result page"""

        history_entry: dict = db.history.find_one({"_id": ObjectId(result_id)})

        # Ensure the history entry exists and belongs to the current user
        if not history_entry or ObjectId(current_user.id) != history_entry["owner"]:
            flash("Audio translation not found", "danger")
            return redirect(url_for("dashboard"))

        # Convert Object Id's into strings for easy display
        history_entry["output_file_id"] = str(history_entry.get("output_file_id"))
        history_entry["owner"] = str(history_entry.get("owner"))

        return render_template("result.html", result=history_entry)

    @app.route("/dashboard")
    @login_required
    def dashboard():
        """Dashboard page for a user"""

        return render_template("dashboard.html")

    @app.route("/history")
    @login_required
    def get_history():
        """History of uses by current user"""

        # Get list of documents representing operations done by the user
        user: dict = db.users.find_one({"_id": ObjectId(current_user.id)})
        result_history: list[dict] = list(
            db.history.find({"_id": {"$in": user.get("history", [])}})
        )

        # Convert Object Id's into strings for easy display
        for history_entry in result_history:
            history_entry["_id"] = str(history_entry["_id"])
            history_entry["output_file_id"] = str(history_entry.get("output_file_id"))
            history_entry["owner"] = str(history_entry.get("owner"))

        return render_template("history.html", history=result_history)

    @app.route("/audio/<audio_id>")
    @login_required
    def get_audio(audio_id: str):
        """Return the audio file requested"""

        result_doc = db.history.find_one({"output_file_id": ObjectId(audio_id)})

        # Ensure audio file exists and belongs to the current user
        if not result_doc or result_doc["owner"] != ObjectId(current_user.id):
            return {"error": "Not found"}, 404

        # Send file to frontend
        file = gridfs.open_download_stream(ObjectId(audio_id))
        contents = file.read()
        return send_file(
            BytesIO(contents), mimetype="audio/wav", download_name=file.filename
        )

    return app
