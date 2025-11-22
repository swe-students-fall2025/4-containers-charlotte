"""Transcriber model unit tests"""

from unittest.mock import MagicMock, patch
import pytest


def test_init_loads_model(transcriber):
    """Transcriber load model unit test"""
    assert transcriber.model_size == "tiny"
    assert transcriber.model.device == "cpu"
    assert transcriber.model.is_multilingual is True


def test_transcribe_file_not_found(transcriber):
    """Transcribe function test with file not existing"""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            transcriber.transcribe("nonexistent.wav")


def test_transcribe_calls_model(transcriber):
    """Transcribe function unit test"""
    mock_result = {"text": "Hello", "language": "en", "segments": []}

    transcriber.model.transcribe = MagicMock(return_value=mock_result)
    with patch("os.path.exists", return_value=True):
        result = transcriber.transcribe("dummy.wav")

    assert result["text"] == "Hello"
    assert result["language"] == "en"
    assert result["segments"] == []
    assert "processing_time" in result
    transcriber.model.transcribe.assert_called_once()


def test_transcribe_with_language_option(transcriber):
    """Transcribe function test with language config"""
    mock_result = {"text": "Bonjour", "language": "fr", "segments": []}

    transcriber.model.transcribe = MagicMock(return_value=mock_result)
    with patch("os.path.exists", return_value=True):
        result = transcriber.transcribe("dummy.wav", language="fr")

    transcriber.model.transcribe.assert_called_once()
    call_args = transcriber.model.transcribe.call_args[1]
    assert call_args["language"] == result["language"]


def test_translate_to_english(transcriber):
    """Translate_to_english function unit test"""
    mock_result = {"text": "Hello", "language": "fr", "segments": []}
    transcriber.model.transcribe = MagicMock(return_value=mock_result)
    with patch("os.path.exists", return_value=True):
        result = transcriber.translate_to_english("dummy.wav")

    assert result["text"] == "Hello"
    assert result["source_language"] == "fr"
    assert result["segments"] == []
    transcriber.model.transcribe.assert_called_once()
    call_args = transcriber.model.transcribe.call_args[1]
    assert call_args["task"] == "translate"


def test_detect_language(transcriber):
    """Detect_language function unit test"""
    mock_probs = {"en": 0.7, "fr": 0.3}

    with patch("os.path.exists", return_value=True), patch(
        "app.models.transcriber.whisper.load_audio", return_value="audio"
    ), patch(
        "app.models.transcriber.whisper.pad_or_trim", side_effect=lambda x: x
    ), patch(
        "app.models.transcriber.whisper.log_mel_spectrogram",
        side_effect=lambda x: MagicMock(to=lambda device: "mel"),
    ):

        transcriber.model.detect_language = MagicMock(return_value=(None, mock_probs))
        lang = transcriber.detect_language("dummy.wav")

    assert lang == "en"
    transcriber.model.detect_language.assert_called_once()


def test_get_model_info(transcriber):
    """Get_model_info function unit test"""
    info = transcriber.get_model_info()
    assert info["model_size"] == "tiny"
    assert info["device"] == "cpu"
    assert info["is_multilingual"] is True
