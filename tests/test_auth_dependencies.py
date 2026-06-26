import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from src.auth.dependencies import verify_jwt, require_role
from src.schemas.common import Role


class TestJWTSignatureVerification:
    @patch("src.auth.dependencies.get_jwks")
    @patch("jose.jwt.get_unverified_header")
    @patch("jose.jwt.decode")
    async def test_valid_jwt_accepted(self, mock_decode, mock_header, mock_jwks):
        mock_jwks.return_value = {
            "keys": [{"kid": "test-kid", "kty": "RSA", "n": "...", "e": "..."}]
        }
        mock_header.return_value = {"kid": "test-kid"}
        mock_decode.return_value = {"sub": "student-123", "aud": "authenticated"}

        result = await verify_jwt("valid.token.here")
        assert result["sub"] == "student-123"
        mock_decode.assert_called_once()

    @patch("src.auth.dependencies.get_jwks")
    @patch("jose.jwt.get_unverified_header")
    async def test_expired_jwt_rejected(self, mock_header, mock_jwks):
        mock_jwks.return_value = {
            "keys": [{"kid": "test-kid", "kty": "RSA", "n": "...", "e": "..."}]
        }
        mock_header.return_value = {"kid": "test-kid"}

        with patch("jose.jwt.decode", side_effect=Exception("Signature verification failed")):
            with pytest.raises(HTTPException) as exc:
                await verify_jwt("expired.token.here")
            assert exc.value.status_code == 401

    @patch("src.auth.dependencies.get_jwks")
    async def test_missing_kid_rejected(self, mock_jwks):
        mock_jwks.return_value = {"keys": [{"kid": "other-kid"}]}

        with patch("jose.jwt.get_unverified_header", return_value={"kid": "unknown-kid"}):
            with pytest.raises(HTTPException) as exc:
                await verify_jwt("token.with.unknown.kid")
            assert exc.value.status_code == 401


class TestRBAC:
    def test_require_role_allows_valid_role(self):
        current_user = {"user_metadata": {"role": "student"}}
        allowed = [Role.STUDENT]

        async def check():
            dep = require_role(allowed)
            result = await dep(current_user)
            assert result == current_user

        import asyncio
        asyncio.run(check())

    def test_require_role_rejects_invalid_role(self):
        current_user = {"user_metadata": {"role": "student"}}
        allowed = [Role.TEACHER, Role.ADMIN]

        async def check():
            dep = require_role(allowed)
            with pytest.raises(HTTPException) as exc:
                await dep(current_user)
            assert exc.value.status_code == 403

        import asyncio
        asyncio.run(check())
