"""
Configuration settings for the ML client app
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Base configurations
    """

    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # MongoDB settings
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB")

    # Transcriber (Whisper) model settings
    TRANSCRIBER_MODEL_SIZE = os.getenv("TRANSCRIBER_MODEL_SIZE", "base")

    # Audio settings
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "outputs")
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024))
    )  # 16MB default
    ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "flac", "ogg"}

    # Processing settings
    DEVICE = os.getenv("DEVICE", "cpu")  # or 'cuda' for GPU

    @staticmethod
    def init_directories():
        """Create necessary directories for file storage."""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

    @staticmethod
    def validate():
        """Validate configuration settings."""
        required_vars = ["SECRET_KEY", "MONGO_URI", "MONGO_DB_NAME"]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        return True
