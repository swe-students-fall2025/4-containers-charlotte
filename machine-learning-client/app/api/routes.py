"""
API endpoints for ML client processing
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app, send_file
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


@api_bp.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """
    Transcribe audio file to text.

    Expects
    -------
    request.files['audio'] : file
        Audio file to transcribe.
    request.form['language'] : str, optional
        Optional language code ('en', 'fr', 'ko', 'zh').

    Returns
    -------
    response : JSON
        Dictionary with transcription results or error message.
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

        # Get optional language parameter
        language = request.form.get("language", None)

        # Process audio (ML work only)
        processor = Processor()
        result = processor.transcribe(upload_path, language=language)

        # Clean up uploaded file
        os.remove(upload_path)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/translate", methods=["POST"])
def translate_audio():
    """
    Translate audio to English text.

    Expects
    -------
    request.files['audio'] : file
        Audio file to translate.

    Returns
    -------
    response : JSON
        Dictionary with translation results or error message.
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

        # Process audio (ML work only)
        processor = Processor()
        result = processor.translate_to_english(upload_path)

        # Clean up uploaded file
        os.remove(upload_path)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Translation error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/voice-clone", methods=["POST"])
def voice_clone():
    """
    Clone voice and synthesize speech.

    Expects
    -------
    request.files['reference_audio'] : file
        Reference audio file for voice cloning.
    request.form['text'] : str
        Text to synthesize.
    request.form['target_language'] : str, optional
        Target language code (default='en').

    Returns
    -------
    response : JSON
        Dictionary with output_path to generated audio or error message.
    """
    try:
        if "reference_audio" not in request.files:
            return jsonify({"error": "No reference audio provided"}), 400

        if "text" not in request.form:
            return jsonify({"error": "No text provided"}), 400

        reference_file = request.files["reference_audio"]
        text = request.form["text"]
        target_language = request.form.get("target_language", "en")

        if reference_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(reference_file.filename):
            return jsonify({"error": "File type not allowed"}), 400

        # Save reference audio
        ref_filename = secure_filename(reference_file.filename)
        ref_path = os.path.join(current_app.config["UPLOAD_FOLDER"], ref_filename)
        reference_file.save(ref_path)

        # Process voice cloning (ML work only)
        processor = Processor()
        output_path = processor.clone_voice(ref_path, text, target_language)

        # Clean up reference file
        os.remove(ref_path)

        # Return the generated audio file
        if not os.path.exists(output_path):
            return jsonify({"error": "Generated audio file not found"}), 500

        return send_file(
            output_path,
            mimetype="audio/wav",
            as_attachment=True,
            download_name=os.path.basename(output_path)
        )

    except Exception as e:
        logger.error(f"Voice cloning error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/download/<path:filename>", methods=["GET"])
def download_audio(filename):
    """
    Download generated audio file.

    Parameters
    ----------
    filename : str
        Name of the file to download.

    Returns
    -------
    response : file or JSON
        Audio file or error message.
    """
    try:
        file_path = os.path.join(current_app.config["OUTPUT_FOLDER"], filename)

        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(file_path, mimetype="audio/wav", as_attachment=True)

    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({"error": str(e)}), 500


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
