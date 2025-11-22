"""Voice Cloner model tests"""

from unittest.mock import MagicMock, patch
import os
from datetime import datetime
import pytest
from app.models.voice_cloner import VoiceCloner


def test_init_creates_output_dir(voice_cloner):
    """Init unit test"""
    with patch("os.makedirs") as makedirs_mock:
        VoiceCloner()
        makedirs_mock.assert_called_once_with(voice_cloner.output_dir, exist_ok=True)


def test_clone_and_speak_empty_text_raises(voice_cloner):
    """Clone and speak raises error unit test"""
    with pytest.raises(ValueError):
        voice_cloner.clone_and_speak("dummy.wav", "")


def test_clone_and_speak_nonexistent_file_raises(voice_cloner):
    """Clone and speak with nonexistent file test"""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            voice_cloner.clone_and_speak("nonexistent.wav", "Hello")


@patch("app.models.voice_cloner.TTS")
@patch("torch.cuda.is_available")
def test_init_model_sets_device_and_model(mock_cuda, mock_tts_class):
    """Init model test setting device and model type"""
    mock_tts_instance = MagicMock()
    mock_tts_class.return_value = mock_tts_instance

    mock_cuda.return_value = False

    vc = VoiceCloner()

    assert vc.device == "cpu"
    assert vc.tts_model == mock_tts_instance.to.return_value
    mock_tts_instance.to.assert_called_once_with("cpu")


def test_clone_and_speak_calls_tts(monkeypatch):
    """Clone and speak test"""
    vc = VoiceCloner()
    vc.tts_model = MagicMock()

    monkeypatch.setattr(
        "app.models.voice_cloner.datetime",
        MagicMock(now=lambda: datetime(2025, 1, 1, 12, 0, 0)),
    )
    monkeypatch.setattr("os.path.exists", lambda path: True)
    output_path = vc.clone_and_speak("dummy.wav", "Hello world")

    expected_path = os.path.join(vc.output_dir, "cloned_voice_20250101_120000.wav")
    assert output_path == expected_path
    vc.tts_model.tts_to_file.assert_called_once_with(
        text="Hello world",
        speaker_wav="dummy.wav",
        language="en",
        file_path=expected_path,
    )


def test_is_available():
    "Is available test"
    vc = VoiceCloner()
    vc.tts_model = MagicMock()
    assert vc.is_available() is True


def test_get_model_info():
    "Get model info test"
    vc = VoiceCloner()
    vc.tts_model = MagicMock()
    vc.device = "cpu"
    info = vc.get_model_info()
    assert info == {"available": True, "device": "cpu", "model_loaded": True}
