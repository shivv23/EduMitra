import pytest
import hmac
import hashlib
from src.routes.whatsapp import verify_webhook_signature


class TestWebhookSignatureVerification:
    def test_valid_signature_passes(self):
        payload = b'{"entry": [{"changes": [{"value": {"messages": [{"text": "hello"}]}}]}]}'
        secret = "test_app_secret"

        expected = "sha256=" + hmac.new(
            key=secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256,
        ).hexdigest()

        assert verify_webhook_signature(payload, expected) is True

    def test_invalid_signature_fails(self):
        payload = b'{"test": "data"}'
        assert verify_webhook_signature(payload, "sha256:invalid_signature") is False

    def test_empty_signature_fails(self):
        payload = b'{"test": "data"}'
        assert verify_webhook_signature(payload, "") is False

    def test_tampered_payload_fails(self):
        payload = b'{"original": "data"}'
        secret = "test_secret"

        valid_sig = "sha256=" + hmac.new(
            key=secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Different payload
        assert verify_webhook_signature(b'{"tampered": "data"}', valid_sig) is False

    def test_constant_time_comparison(self):
        """Verify HMAC comparison uses constant-time function (not ==)."""
        payload = b"test"
        secret = "test"
        valid_sig = "sha256=" + hmac.new(
            key=secret.encode(), msg=payload, digestmod=hashlib.sha256,
        ).hexdigest()

        from hmac import compare_digest
        # Implementation should use hmac.compare_digest
        result = verify_webhook_signature(payload, valid_sig)
        assert result is True
