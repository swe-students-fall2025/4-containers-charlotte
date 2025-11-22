"""API Tests for app connection to ML Client"""

from unittest.mock import patch, MagicMock
import io
from bson import ObjectId


def test_upload_post_success(client, mock_db, mock_ml_client_response):
    """Test /upload route POST success"""
    # file with correct MIME type
    fake_file = (io.BytesIO(b"hello"), "audio.wav", "audio/wav")
    # patch DB insert to return a fake inserted_id
    fake_id = ObjectId("6921729aaf0d7a28740f29d9")
    mock_db.history.insert_one.return_value = MagicMock(inserted_id=fake_id)

    print(fake_id, mock_db.history.insert_one.return_value.inserted_id)

    # patch ML client
    with patch("app.requests.post", return_value=mock_ml_client_response):

        with patch("app.current_user") as mock_user:
            mock_user.id = str(ObjectId())

            res = client.post(
                "/upload",
                data={"audio": fake_file},
                content_type="multipart/form-data",
            )

    assert res.status_code == 302
    assert f"/result/{fake_id}" in res.headers["Location"]


def test_result_page_success(client, mock_db):
    """Test /result unit test with success"""
    # the fixture's history.find_one() returns this structure:
    entry = mock_db.history.find_one.return_value
    result_id = entry["_id"]
    owner_id = entry["owner"]

    with patch("app.current_user") as mock_user:
        mock_user.id = str(owner_id)  # match the owner

        res = client.get(f"/result/{result_id}")

    assert res.status_code == 200
    assert b"Hello" in res.data


def test_result_page_wrong_owner(client, mock_db):
    """Tests /result/id with wrong owner"""
    entry = mock_db.history.find_one.return_value
    result_id = entry["_id"]

    with patch("app.current_user") as mock_user:
        mock_user.id = str(ObjectId())  # mismatch

        res = client.get(f"/result/{result_id}")

    assert res.status_code == 302
    assert "/dashboard" in res.location
