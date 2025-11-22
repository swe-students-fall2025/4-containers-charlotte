"""Mock fixtures for unit tests"""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

# patch ML models and dependencies
patch_whisper = patch("app.models.transcriber.whisper", MagicMock())
patch_torch = patch("app.models.voice_cloner.torch", MagicMock(return_value="cpu"))
patch_tts = patch("app.models.voice_cloner.TTS", None)
patch_config = patch("app.models.voice_cloner.Config.OUTPUT_FOLDER", "/tmp/test_output")

# Start all patches
patch_whisper.start()
patch_torch.start()
patch_tts.start()
patch_config.start()

# pylint: disable=wrong-import-position
from app.api.routes import api_bp
from app.models.transcriber import Transcriber
from app.models.voice_cloner import VoiceCloner
from app.services.processor import Processor


@pytest.fixture
def voice_cloner():
    """Mock voice_cloner model"""
    vc = VoiceCloner()
    return vc


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
