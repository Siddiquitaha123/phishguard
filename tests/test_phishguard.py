import pytest

from app.analyzer import MAX_INPUT_LENGTH, analyze, extract_urls
from app.main import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_extract_urls_deduplicates_and_normalizes_www():
    assert extract_urls("Visit www.example.com and www.example.com now.") == ["http://www.example.com"]


def test_high_risk_message_is_explainable():
    result = analyze("URGENT: verify your password immediately at http://192.0.2.10/login?password=x")
    assert result.verdict == "High risk"
    assert result.score >= 60
    assert {finding.code for finding in result.findings} >= {"IP_HOST", "PLAIN_HTTP", "URGENCY", "SENSITIVE_REQUEST"}
    assert all(finding.detail for finding in result.findings)


def test_benign_text_does_not_create_false_high_risk():
    result = analyze("Team meeting is on Tuesday at 10:00. No link included.")
    assert result.verdict == "Low risk"
    assert result.score == 0


def test_api_rejects_bad_content_type(client):
    response = client.post("/api/analyze", data="hello")
    assert response.status_code == 415


def test_api_rejects_empty_text(client):
    response = client.post("/api/analyze", json={"text": " "})
    assert response.status_code == 400


def test_api_enforces_input_limit(client):
    response = client.post("/api/analyze", json={"text": "x" * (MAX_INPUT_LENGTH + 1)})
    assert response.status_code == 413


def test_api_returns_findings_and_headers(client):
    response = client.post("/api/analyze", json={"text": "http://example.com"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["urls"] == ["http://example.com"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
