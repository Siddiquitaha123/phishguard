"""PhishGuard web application."""
from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from .analyzer import MAX_INPUT_LENGTH, analyze


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=MAX_INPUT_LENGTH + 2_000, JSON_SORT_KEYS=False)

    @app.after_request
    def add_security_headers(response):
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; form-action 'self'; base-uri 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/analyze")
    def api_analyze():
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json."}), 415
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
            return jsonify({"error": "Send a JSON object with a string field named 'text'."}), 400
        text = payload["text"]
        if not text.strip():
            return jsonify({"error": "Text cannot be empty."}), 400
        if len(text) > MAX_INPUT_LENGTH:
            return jsonify({"error": f"Text exceeds the {MAX_INPUT_LENGTH:,}-character limit."}), 413
        return jsonify(analyze(text).to_dict())

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify({"error": "Request is too large."}), 413

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
