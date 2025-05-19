import time
import requests
from flask import Blueprint, request, jsonify, current_app
from PIL import Image, UnidentifiedImageError
from .classifier import classify_image

views = Blueprint('views', __name__)

start_time = time.time()
processed = {"success": 0, "fail": 0}

@views.route('/status', methods=['GET'])
def status():
    uptime = round(time.time() - start_time, 2)
    try:
        # Load a known-good local test image (e.g., from disk or memory)
        with open("website/test_image.jpg", "rb") as f:
            files = {'image': ('test_image.jpg', f, 'image/jpeg')}
            headers = {'X-Internal-Check': 'true'}
            port = current_app.config['PORT']

            response = requests.post(
                f"http://localhost:{port}/upload_image",
                files=files,
                headers=headers
            )

        classifier_health = "ok" if response.status_code == 200 else "error"

    except Exception as e:
        current_app.logger.error(f"Health check failed: {e}")
        classifier_health = "error"

    return jsonify({
        "status": {
            "uptime": uptime,
            "processed": {
                "success": processed["success"],
                "fail": processed["fail"]
            },
            "health": classifier_health,
            "api_version": 1
        }
    }), 200


@views.route('/upload_image', methods=['POST'])
def upload_image():

    if 'image' not in request.files:
        return error_response(400, "Missing image field")

    file = request.files['image']
    is_internal_check = request.headers.get('X-Internal-Check') == 'true'

    try:
        # Try to decode the image — raise if invalid
        try:
            img = Image.open(file.stream)
            img.verify()  # Validate image structure
        except Exception:
            raise UnidentifiedImageError()

        # Rewind and reopen the image (verify() consumes the stream)
        file.stream.seek(0)
        img = Image.open(file.stream)

        print(f"[INFO] Received image of format: {img.format}")

        matches = classify_image(img)
        if not is_internal_check:
            processed["success"] += 1
        return jsonify({"matches": matches}), 200

    except UnidentifiedImageError:
        if not is_internal_check:
            processed["fail"] += 1
        return error_response(400, "Unsupported image format")

    except Exception:
        if not is_internal_check:
            processed["fail"] += 1
        return error_response(500, "Internal server error")


@views.route('/upload_image', methods=['GET', 'PUT', 'DELETE', 'PATCH'])
def wrong_method():
    return error_response(405, "Unsupported method")


def error_response(code, message):
    return jsonify({
        "error": {
            "http_status": code,
            "message": message
        }
    }), code
