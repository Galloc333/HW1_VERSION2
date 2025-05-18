import time
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from .classifier import classify_image

views = Blueprint('views', __name__)

start_time = time.time()
processed = {"success": 0, "fail": 0}
classifier_health = {"status": "ok"}  # Can be 'ok' or 'error'


@views.route('/status', methods=['GET'])
def status():
    uptime = round(time.time() - start_time, 2)

    return jsonify({
        "status": {
            "uptime": uptime,
            "processed": {
                "success": processed["success"],
                "fail": processed["fail"]
            },
            "health": classifier_health["status"],
            "api_version": 1
        }
    }), 200


@views.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return error_response(400, "Missing image field")

    file = request.files['image']
    filename = secure_filename(file.filename)

    try:
        # Try to decode the image — raise if invalid
        try:
            img = Image.open(file)
            img.verify()  # Validate image structure
        except Exception:
            raise UnidentifiedImageError()

        # Rewind and reopen the image (verify() consumes the stream)
        file.stream.seek(0)
        img = Image.open(file)

        print(f"[INFO] Received image of format: {img.format}")

        # Measure classification time
        start = time.time()
        matches = classify_image(img)
        duration = time.time() - start

        if duration > 10:  # Simulate too-slow classification (NEED TO CHANGE)
            raise Exception("Processing took too long")

        processed["success"] += 1
        return jsonify({"matches": matches}), 200

    except UnidentifiedImageError:
        processed["fail"] += 1
        return error_response(400, "Unsupported image format")

    except Exception:
        #classifier_health["status"] = "error"
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
