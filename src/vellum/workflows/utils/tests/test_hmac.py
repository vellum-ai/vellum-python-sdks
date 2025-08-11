import os
from unittest.mock import patch

from requests import Request

from vellum.workflows.utils.hmac import _sign_request, sign_request_with_env_secret


class TestHMACUtils:
    def test_sign_request_adds_headers(self):
        """Test that _sign_request adds the correct HMAC headers."""
        request = Request(method="POST", url="https://example.com", json={"test": "data"}).prepare()
        secret = "test-secret"

        with patch("time.time", return_value=1234567890):
            _sign_request(request, secret)

        assert "X-Vellum-Timestamp" in request.headers
        assert "X-Vellum-Signature" in request.headers
        assert request.headers["X-Vellum-Timestamp"] == "1234567890"
        assert len(request.headers["X-Vellum-Signature"]) == 64

    def test_sign_request_with_string_body(self):
        """Test HMAC signing with string body data."""
        request = Request(method="POST", url="https://example.com", data="test data").prepare()
        secret = "test-secret"

        _sign_request(request, secret)

        assert "X-Vellum-Timestamp" in request.headers
        assert "X-Vellum-Signature" in request.headers

    def test_sign_request_with_no_body(self):
        """Test HMAC signing with no body."""
        request = Request(method="GET", url="https://example.com").prepare()
        secret = "test-secret"

        _sign_request(request, secret)

        assert "X-Vellum-Timestamp" in request.headers
        assert "X-Vellum-Signature" in request.headers

    def test_sign_request_with_env_secret_present(self):
        """Test that sign_request_with_env_secret works when environment variable is set."""
        request = Request(method="POST", url="https://example.com").prepare()

        with patch.dict(os.environ, {"VELLUM_HMAC_SECRET": "env-secret"}):
            sign_request_with_env_secret(request)

        assert "X-Vellum-Timestamp" in request.headers
        assert "X-Vellum-Signature" in request.headers

    def test_sign_request_with_env_secret_absent(self):
        """Test that sign_request_with_env_secret does nothing when environment variable is not set."""
        request = Request(method="POST", url="https://example.com").prepare()
        original_headers = dict(request.headers)

        with patch.dict(os.environ, {}, clear=True):
            sign_request_with_env_secret(request)

        assert "X-Vellum-Timestamp" not in request.headers
        assert "X-Vellum-Signature" not in request.headers
        assert dict(request.headers) == original_headers
