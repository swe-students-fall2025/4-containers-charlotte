"""Mock fixtures for unit tests"""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from app.api.routes import api_bp
from app.models.transcriber import Transcriber
from app.models.voice_cloner import VoiceCloner
from app.services.processor import Processor


@pytest.fixture
def voice_cloner():
    """Mock voice_cloner model"""
    with patch("app.models.voice_cloner.TTS", None):
        with patch("app.models.voice_cloner.Config.OUTPUT_FOLDER", "/tmp/test_output"):
            yield VoiceCloner()


@pytest.fixture
def transcriber():
    """Mock transcriber model"""
    with patch("app.models.transcriber.whisper.load_model") as mock_load_model:
        mock_model = MagicMock()
        mock_model.device = "cpu"
        mock_model.is_multilingual = True
        mock_load_model.return_value = mock_model
        yield Transcriber(model_size="tiny")


@pytest.fixture
def client():
    """Mock api client"""
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = "/tmp"
    app.register_blueprint(api_bp)
    app.testing = True
    return app.test_client()


@pytest.fixture
def mock_ml_client():
    """Mock ML-Client Processor"""
    ml_client = Processor()
    ml_client.transcriber = MagicMock()
    ml_client.voice_cloner = MagicMock()
    return ml_client
