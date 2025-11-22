"""Processor service unit tests"""

from unittest.mock import MagicMock, patch


def test_transcribe(mock_ml_client):
    """Test transcribe function"""
    mock_result = {
        "text": "hello world",
        "language": "en",
        "segments": [],
        "processing_time": 1.2,
    }
    mock_ml_client.transcriber.transcribe.return_value = mock_result

    result = mock_ml_client.transcribe("audio.mp3")

    # Check the result
    assert result["text"] == "hello world"
    assert result["language"] == "en"
    assert result["audio_path"] == "audio.mp3"
    assert "timestamp" in result


def test_translate_to_english(mock_ml_client):
    """Test translate_to_english function"""
    mock_result = {
        "text": "hello world",
        "source_language": "fr",
        "segments": [],
        "processing_time": 1.5,
    }
    mock_ml_client.transcriber.translate_to_english.return_value = mock_result

    result = mock_ml_client.translate_to_english("audio.mp3")

    assert result["text"] == "hello world"
    assert result["source_language"] == "fr"
    assert result["audio_path"] == "audio.mp3"
    assert "timestamp" in result


def test_clone_voice(mock_ml_client):
    """Test clone_voice function"""
    mock_ml_client.voice_cloner.clone_and_speak.return_value = "output.mp3"
    output_path = mock_ml_client.clone_voice("ref.mp3", "Hello", target_language="en")
    assert output_path == "output.mp3"


@patch("builtins.open")
@patch("os.remove")
@patch("app.services.processor.gridfs.upload_from_stream")
def test_process_audio_file(mock_upload, mock_remove, mock_open, mock_ml_client):
    """Test process_audio_file function wiht mocks"""
    mock_open.new_callable = MagicMock()

    # Mock translation
    mock_ml_client.translate_to_english = MagicMock(
        return_value={"text": "Hello", "source_language": "fr", "processing_time": 2.0}
    )
    # Mock voice cloning
    mock_ml_client.clone_voice = MagicMock(return_value="output.mp3")
    # Mock GridFS
    mock_upload.return_value = "mock_file_id"

    result = mock_ml_client.process_audio_file("audio.mp3")

    # Assertions
    assert result["original_audio_path"] == "audio.mp3"
    assert result["source_language"] == "fr"
    assert result["english_text"] == "Hello"
    assert result["output_file_id"] == "mock_file_id"
    assert result["processing_time"] == 2.0

    mock_ml_client.translate_to_english.assert_called_once_with("audio.mp3")
    mock_ml_client.clone_voice.assert_called_once_with(
        reference_audio="audio.mp3", text="Hello", target_language="en"
    )
    mock_upload.assert_called_once()
    mock_remove.assert_called_once_with("output.mp3")
