"""
test_main.py
============
Test suite for the Containerized Python API.

Uses FastAPI's built-in TestClient (powered by httpx / requests) to exercise
every endpoint and the core generate() utility function.

Run with:
    pytest test_main.py -v
"""

import hashlib
import pytest
from fastapi.testclient import TestClient

from main import app, generate

# ---------------------------------------------------------------------------
# Test client fixture
# ---------------------------------------------------------------------------
client = TestClient(app)


# ===========================================================================
# Tests for the generate() utility function
# ===========================================================================

class TestGenerateFunction:
    """Unit tests for the generate() helper function."""

    def test_generate_returns_string(self):
        """generate() should always return a string."""
        result = generate("hello")
        assert isinstance(result, str)

    def test_generate_returns_64_char_hex(self):
        """SHA-256 hex digest is exactly 64 characters long."""
        result = generate("hello")
        assert len(result) == 64

    def test_generate_known_value(self):
        """generate() must produce the correct SHA-256 digest."""
        expected = hashlib.sha256(b"hello").hexdigest()
        assert generate("hello") == expected

    def test_generate_empty_string(self):
        """generate() should handle an empty string without error."""
        expected = hashlib.sha256(b"").hexdigest()
        assert generate("") == expected

    def test_generate_deterministic(self):
        """Calling generate() twice with the same input yields the same result."""
        assert generate("test") == generate("test")

    def test_generate_different_inputs_differ(self):
        """Different inputs must produce different digests."""
        assert generate("foo") != generate("bar")

    def test_generate_unicode(self):
        """generate() should handle unicode text correctly."""
        text = "こんにちは"
        expected = hashlib.sha256(text.encode()).hexdigest()
        assert generate(text) == expected


# ===========================================================================
# Tests for GET /  (welcome page)
# ===========================================================================

class TestWelcomeEndpoint:
    """Tests for the HTML welcome page."""

    def test_welcome_status_200(self):
        """GET / should return HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_welcome_returns_html(self):
        """GET / should return HTML content type."""
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_welcome_contains_name(self):
        """The welcome page must display the participant's name."""
        response = client.get("/")
        assert "Jaya Narayana" in response.text  # update if you change the name

    def test_welcome_contains_rocket(self):
        """The welcome page should contain the rocket emoji."""
        response = client.get("/")
        assert "🚀" in response.text

    def test_welcome_contains_api_title(self):
        """The welcome page should mention the API name."""
        response = client.get("/")
        assert "Containerized Python API" in response.text


# ===========================================================================
# Tests for GET /token
# ===========================================================================

class TestTokenEndpoint:
    """Tests for the original single-token endpoint."""

    def test_token_status_200(self):
        """GET /token should return HTTP 200."""
        response = client.get("/token")
        assert response.status_code == 200

    def test_token_returns_json(self):
        """GET /token should return a JSON object."""
        response = client.get("/token")
        data = response.json()
        assert isinstance(data, dict)

    def test_token_has_token_key(self):
        """Response JSON must contain a 'token' key."""
        response = client.get("/token")
        assert "token" in response.json()

    def test_token_value_is_64_chars(self):
        """The token value should be a 64-character hex string."""
        response = client.get("/token")
        assert len(response.json()["token"]) == 64

    def test_token_value_is_deterministic(self):
        """The token endpoint should return the same value on repeated calls."""
        r1 = client.get("/token").json()["token"]
        r2 = client.get("/token").json()["token"]
        assert r1 == r2

    def test_token_correct_value(self):
        """The token must equal SHA-256('token')."""
        expected = hashlib.sha256(b"token").hexdigest()
        response = client.get("/token")
        assert response.json()["token"] == expected


# ===========================================================================
# Tests for POST /generate
# ===========================================================================

class TestGenerateEndpoint:
    """Tests for the new /generate endpoint."""

    def test_generate_status_200(self):
        """POST /generate should return HTTP 200 for valid input."""
        response = client.post("/generate", json={"text": "hello"})
        assert response.status_code == 200

    def test_generate_returns_json(self):
        """POST /generate should return a JSON object."""
        response = client.post("/generate", json={"text": "hello"})
        assert isinstance(response.json(), dict)

    def test_generate_response_has_text_key(self):
        """Response should echo back the original 'text' field."""
        response = client.post("/generate", json={"text": "hello"})
        assert "text" in response.json()

    def test_generate_response_has_checksum_key(self):
        """Response should contain a 'checksum' key."""
        response = client.post("/generate", json={"text": "hello"})
        assert "checksum" in response.json()

    def test_generate_echoes_text(self):
        """The 'text' field in the response must match the input."""
        response = client.post("/generate", json={"text": "FastAPI is great"})
        assert response.json()["text"] == "FastAPI is great"

    def test_generate_checksum_correct(self):
        """Checksum must equal SHA-256 of the provided text."""
        text = "Hello, World!"
        expected = hashlib.sha256(text.encode()).hexdigest()
        response = client.post("/generate", json={"text": text})
        assert response.json()["checksum"] == expected

    def test_generate_empty_text(self):
        """POST /generate should handle empty string text."""
        response = client.post("/generate", json={"text": ""})
        assert response.status_code == 200
        expected = hashlib.sha256(b"").hexdigest()
        assert response.json()["checksum"] == expected

    def test_generate_missing_text_field_returns_422(self):
        """POST /generate with missing 'text' should return HTTP 422."""
        response = client.post("/generate", json={})
        assert response.status_code == 422

    def test_generate_wrong_field_name_returns_422(self):
        """POST /generate with wrong field name should return HTTP 422."""
        response = client.post("/generate", json={"input": "hello"})
        assert response.status_code == 422

    def test_generate_unicode_text(self):
        """POST /generate should correctly process unicode text."""
        text = "こんにちは"
        expected = hashlib.sha256(text.encode()).hexdigest()
        response = client.post("/generate", json={"text": text})
        assert response.status_code == 200
        assert response.json()["checksum"] == expected

    def test_generate_long_text(self):
        """POST /generate should handle long strings without error."""
        text = "A" * 10_000
        expected = hashlib.sha256(text.encode()).hexdigest()
        response = client.post("/generate", json={"text": text})
        assert response.status_code == 200
        assert response.json()["checksum"] == expected

    def test_generate_different_inputs_different_checksums(self):
        """Different inputs must produce different checksums."""
        r1 = client.post("/generate", json={"text": "foo"}).json()["checksum"]
        r2 = client.post("/generate", json={"text": "bar"}).json()["checksum"]
        assert r1 != r2
