"""Flask app"""

import os
import pathlib
from typing import Optional

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

import models
from auth import auth_bp
from db import get_users_collection, get_history_collection


from flask import send_from_directory, request, jsonify
import requests


DIR = pathlib.Path(__file__).parent

# Load environment variables
load_dotenv(DIR / ".env", override=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[models.User]:
    """Load currently logged-in user data"""

    users = get_users_collection()
    user_data = users.find_one({"_id": ObjectId(user_id)})

    if not user_data:
        return None

    return models.User(user_data)


# Register auth blueprint
app.register_blueprint(auth_bp)


@app.route("/")
def index():
    """Landing page"""

    return "Web App Running"

@app.route("/upload")
def upload_page():
    return send_from_directory("static", "upload.html")


@app.route("/result")
def result_page():
    return send_from_directory("static", "result.html")


@app.route("/history")
def history_page():
    return send_from_directory("static", "history.html")


ML_URL = "http://machine-learning-client:5001"  # adjust if needed

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Receives file from frontend -> forwards to ML service -> returns JSON"""

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    target_lang = request.form.get("target_language", "en")

    # forward to ML client
    files = {"file": (file.filename, file.stream, file.mimetype)}
    data = {"target_language": target_lang}

    try:
        ml_resp = requests.post(f"{ML_URL}/process", files=files, data=data, timeout=120)
        ml_data = ml_resp.json()
    except Exception as e:
        return jsonify({"error": f"ML Service Error: {str(e)}"}), 500

    # log history
    coll = get_history_collection()
    coll.insert_one(
        {
            "user_id": ObjectId(request.form.get("user_id")) if request.form.get("user_id") else None,
            "original_filename": file.filename,
            "transcript": ml_data.get("transcript"),
            "translation": ml_data.get("translation"),
            "audio_url": ml_data.get("audio_url"),
            "created_at": ml_data.get("created_at"),
        }
    )

    return jsonify(ml_data)

@app.route("/api/history")
def api_history():
    """Returns full history list"""
    coll = get_history_collection()
    docs = list(coll.find().sort("created_at", -1))

    # convert ObjectId
    for d in docs:
        d["_id"] = str(d["_id"])

    return jsonify(docs)



if __name__ == "__main__":
    app.run(debug=True)
