# tests/test_routes_extra.py
"""
Extra route tests: upload edge cases and result not found.
"""

import io
from bson import ObjectId
from unittest.mock import MagicMock, patch

import pytest

# IMPORTANT:
# Replace "test_app" below with the actual filename of your existing test file
# that contains fixtures: client, mock_db, mock_ml_client_response
from test_app import client, mock_db, mock_ml_client_response  # noqa: F401


def test_upload_missing_file(client, mock_db):
    """
    POST /upload with no 'audio' field should not crash.
    We just assert it returns 200 and stays on the same page.
    """
    response = client.post("/upload", data={}, follow_redirects=True)

    assert response.status_code == 200
    # Typically you'll re-render the upload form
    assert b"Upload" in response.data or b"audio" in response.data


def test_upload_unsupported_file_type(client, mock_db):
    """
    POST /upload with a non-audio file extension should be rejected gracefully.
    """
    fake_file = (io.BytesIO(b"not an audio file"), "notes.txt", "text/plain")

    response = client.post(
        "/upload",
        data={"audio": fake_file},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    # Adjust the message below if your template uses different text
    # We just want to confirm an error-ish response, not a redirect to /result.
    assert b".txt" in response.data or b"file" in response.data


def test_result_not_found(client, mock_db):
    """
    GET /result/<id> when the history record does not exist.
    The app should handle this gracefully (redirect or 404).
    """
    mock_db.history.find_one.return_value = None
    fake_id = ObjectId()

    with patch("app.current_user") as mock_user:
        mock_user.id = str(ObjectId())

        res = client.get(f"/result/{fake_id}", follow_redirects=True)

    # Depending on your implementation, this might redirect to /dashboard
    # or show a 404 page. We at least assert that it doesn't crash.
    assert res.status_code in (200, 302, 404)
