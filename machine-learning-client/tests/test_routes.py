"""Test for api route"""

import io
import os
from unittest.mock import patch, MagicMock


def test_process_no_file(client):
    """Process function without file test"""
    response = client.post("/process", data={})
    assert response.status_code == 400
    assert response.json == {"error": "No audio file provided"}


def test_process_empty_filename(client):
    """Process function empty filename test"""
    data = {"audio": (io.BytesIO(b"dummy data"), "")}
    response = client.post("/process", data=data)
    assert response.status_code == 400
    assert response.json == {"error": "No file selected"}


@patch("app.api.routes.allowed_file", return_value=False)
def test_process_disallowed_file(mock_allowed_file, client):
    """Process test with disallowed file type"""
    data = {"audio": (io.BytesIO(b"dummy data"), "test.txt")}
    response = client.post("/process", data=data)
    assert response.status_code == 400
    assert response.json == {"error": "File type not allowed"}
    mock_allowed_file.assert_called_once_with("test.txt")


@patch("app.api.routes.Processor")
@patch("os.remove")
@patch("app.api.routes.allowed_file")
def test_process_success(mock_allowed_file, mock_remove, mock_processor_class, client):
    """Process function unit test"""
    # Mock processor
    mock_processor = MagicMock()
    mock_processor.process_audio_file.return_value = {
        "text": "Hello",
        "audio_id": "123",
    }
    mock_processor_class.return_value = mock_processor

    mock_allowed_file.return_value = True

    # Simulate file upload
    data = {"audio": (io.BytesIO(b"dummy audio content"), "test.wav")}
    response = client.post("/process", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.json == {"text": "Hello", "audio_id": "123"}

    # Check processor was called with correct path
    uploaded_path = os.path.join("/tmp", "test.wav")
    mock_processor.process_audio_file.assert_called_once_with(uploaded_path)

    # Ensure file cleanup attempted
    mock_remove.assert_called_once_with(uploaded_path)


@patch("app.api.routes.Processor")
@patch("os.remove")
@patch("app.api.routes.allowed_file")
def test_process_processor_exception(
    mock_allowed_file, mock_remove, mock_processor_class, client
):
    """Process function test where Processor raises exception"""
    # Processor raises an exception
    mock_processor = MagicMock()
    mock_processor.process_audio_file.side_effect = Exception("Processing failed")
    mock_processor_class.return_value = mock_processor

    mock_allowed_file.return_value = True

    mock_remove.side_effect = Exception("Remove failed")

    data = {"audio": (io.BytesIO(b"dummy audio content"), "test.wav")}
    response = client.post("/process", data=data, content_type="multipart/form-data")

    assert response.status_code == 500
    assert "Processing failed" in response.json["error"]
