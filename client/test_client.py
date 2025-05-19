import os
import pytest
from flask import Flask
from server.website import views

# ----------------------
# Pytest fixtures
# ----------------------

@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super-secret-key'
    app.register_blueprint(views)
    return app

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

# ----------------------
# Tests
# ----------------------

def test_status_initial(client):
    response = client.get('/status')

    # Required: HTTP 200 and JSON content
    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    # Required: top-level must be {"status": {...}}
    assert set(data.keys()) == {"status"}

    status = data["status"]

    # Required fields in the correct format (no more, no less)
    assert set(status.keys()) == {
        "uptime",
        "processed",
        "health",
        "api_version"
    }

    # api_version must equal 1 (type-agnostic comparison)
    assert str(status["api_version"]) == "1"

    # health must be "ok" or "error" exactly
    assert status["health"] in {"ok", "error"}

    # processed must contain exactly "success" and "fail"
    assert set(status["processed"].keys()) == {"success", "fail"}


def test_status_counters_change_after_upload(client):
    # Locate the test image relative to this test file
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "assets", "test_image.jpg")

    # Get original status
    response = client.get("/status")
    assert response.status_code == 200
    original_status = response.get_json()["status"]
    orig_success = original_status["processed"]["success"]
    orig_fail = original_status["processed"]["fail"]

    # Upload the image
    with open(path, "rb") as f:
        client.post(
            "/upload_image",
            data={"image": (f, "test_image.jpg")},
            content_type="multipart/form-data"
        )

    # Check new status
    new_status = client.get("/status").get_json()["status"]
    new_success = new_status["processed"]["success"]
    new_fail = new_status["processed"]["fail"]

    # Ensure exactly one counter increased
    delta_success = new_success - orig_success
    delta_fail = new_fail - orig_fail

    assert (delta_success, delta_fail) in [(1, 0), (0, 1)]



def test_wrong_method(client):
    response = client.get("/upload_image")
    assert response.status_code == 405
    assert response.is_json
    data = response.get_json()
    assert "error" in data
    assert data["error"]["http_status"] == 405


def test_upload_valid_image(client):
    base_dir = os.path.dirname(__file__)  # <- this is the path of test_client.py
    path = os.path.join(base_dir, "assets", "test_image.jpg")

    #assert os.path.isfile(path), f"Test image not found at {path}"
    with open(path, "rb") as f:
        response = client.post("/upload_image",
            data={"image": (f, "test_image.jpg")},
            content_type="multipart/form-data"
        )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.get_json()
        assert "matches" in data
        assert len(data["matches"]) >= 1
        sum = 0.0
        for match in data["matches"]:
            assert isinstance(match["name"], str)
            assert 0.0 < match["score"] <= 1.0
            sum += match["score"]
        assert 0.0 < sum <= 1.0
    else:
        data = response.get_json()
        assert "error" in data
        assert data["error"]["http_status"] == 500


def test_upload_invalid_file(client):
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "assets", "invalid_file.txt")
    with open(path, "rb") as f:
        response = client.post("/upload_image",
            data={"image": (f, "invalid_file.txt")},
            content_type="multipart/form-data"
        )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"]["http_status"] == 400



