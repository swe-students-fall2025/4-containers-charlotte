"""
API endpoints for ML client processing
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services.processor import Processor

api_bp = Blueprint("api", __name__)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """
    Check if file extension is allowed.

    Parameters
    ----------
    filename : str
        Name of the file to check.

    Returns
    -------
    allowed : bool
        True if file extension is allowed, False otherwise.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@api_bp.route("/process", methods=["POST"])
def process():
    """
    Complete workflow: translate audio and clone voice.

    Expects
    -------
    request.files['audio'] : file
        Audio file to process.

    Returns
    -------
    response : JSON
        Dictionary with translation text and clone-translated audio file ID.
    """
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]

        if audio_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(audio_file.filename):
            return jsonify({"error": "File type not allowed"}), 400

        # Save uploaded file
        filename = secure_filename(audio_file.filename)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        audio_file.save(upload_path)

        # Process complete workflow
        processor = Processor()
        result = processor.process_audio_file(upload_path)

        # Clean up uploaded file
        os.remove(upload_path)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 500
