"""Tests for security/tokens.py — JWT minting and decoding."""

import time
from unittest.mock import MagicMock

import jwt
import pytest

from studyos_api.security.tokens import decode_access_token, mint_access_token


@pytest.mark.unit
class TestMintAccessToken:
    """Test JWT access token generation."""

    def test_mints_valid_token(self):
        """Creates a decodable JWT with expected claims."""
        settings = MagicMock(
            jwt_secret="test-secret-that-is-at-least-32-chars-long!!",
            jwt_issuer="studyos-api",
            jwt_algorithm="HS256",
            access_token_ttl_seconds=900,
        )

        token = mint_access_token(settings, sub="user-123", roles=["student"])

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_expected_claims(self):
        """Token payload includes sub, roles, iss, typ, iat, exp."""
        settings = MagicMock(
            jwt_secret="test-secret-that-is-at-least-32-chars-long!!",
            jwt_issuer="studyos-api",
            jwt_algorithm="HS256",
            access_token_ttl_seconds=900,
        )

        token = mint_access_token(settings, sub="user-456", roles=["student", "teacher"])
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])

        assert payload["sub"] == "user-456"
        assert payload["roles"] == ["student", "teacher"]
        assert payload["iss"] == "studyos-api"
        assert payload["typ"] == "access"
        assert "iat" in payload
        assert "exp" in payload

    def test_token_expiry_is_correct(self):
        """Token expires after access_token_ttl_seconds."""
        settings = MagicMock(
            jwt_secret="test-secret-that-is-at-least-32-chars-long!!",
            jwt_issuer="studyos-api",
            jwt_algorithm="HS256",
            access_token_ttl_seconds=600,
        )

        before = int(time.time())
        token = mint_access_token(settings, sub="user-789", roles=["student"])
        after = int(time.time())

        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        exp = payload["exp"]

        assert exp >= before + 600
        assert exp <= after + 600

    def test_token_signed_with_hs256(self):
        """Token uses HS256 algorithm."""
        settings = MagicMock(
            jwt_secret="test-secret-that-is-at-least-32-chars-long!!",
            jwt_issuer="studyos-api",
            jwt_algorithm="HS256",
            access_token_ttl_seconds=900,
        )

        token = mint_access_token(settings, sub="user-123", roles=["student"])
        header = jwt.get_unverified_header(token)

        assert header["alg"] == "HS256"

    def test_different_secrets_produce_different_tokens(self):
        """Different JWT secrets produce different tokens."""
        settings1 = MagicMock(
            jwt_secret="secret-one-that-is-at-least-32-chars-long!!",
            jwt_issuer="studyos-api",
            jwt_algorithm="HS256",
            access_token_ttl_seconds=900,
        )
        settings2 = MagicMock(
            jwt_secret="secret-two-that-is-at-least-32-chars-long!!",
            jwt_issuer="studyos-api",
            jwt_algorithm="HS256",
            access_token_ttl_seconds=900,
        )

        token1 = mint_access_token(settings1, sub="user-123", roles=["student"])
        token2 = mint_access_token(settings2, sub="user-123", roles=["student"])

        assert token1 != token2


@pytest.mark.unit
class TestDecodeAccessToken:
    """Test JWT access token decoding and validation."""

    def _make_settings(self, secret="test-secret-that-is-at-least-32-chars-long!!"):
        return MagicMock(
            jwt_secret=secret,
            jwt_issuer="studyos-api",
            jwt_algorithm="HS256",
            access_token_ttl_seconds=900,
        )

    def test_decodes_valid_token(self):
        """Successfully decodes a valid token."""
        settings = self._make_settings()
        token = mint_access_token(settings, sub="user-123", roles=["student"])

        result = decode_access_token(token, settings)

        assert result is not None
        assert result["sub"] == "user-123"
        assert result["roles"] == ["student"]
        assert result["typ"] == "access"

    def test_returns_none_for_expired_token(self):
        """Returns None for expired tokens."""
        settings = self._make_settings()

        # Manually create an expired token
        now = int(time.time())
        payload = {
            "iss": settings.jwt_issuer,
            "sub": "user-123",
            "roles": ["student"],
            "typ": "access",
            "iat": now - 2000,
            "exp": now - 1000,  # Expired 1000 seconds ago
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        result = decode_access_token(token, settings)

        assert result is None

    def test_returns_none_for_wrong_issuer(self):
        """Returns None when issuer doesn't match."""
        settings = self._make_settings()
        token = mint_access_token(settings, sub="user-123", roles=["student"])

        wrong_settings = self._make_settings()
        wrong_settings.jwt_issuer = "wrong-issuer"

        result = decode_access_token(token, wrong_settings)

        assert result is None

    def test_returns_none_for_wrong_secret(self):
        """Returns None when signing secret doesn't match."""
        settings = self._make_settings()
        token = mint_access_token(settings, sub="user-123", roles=["student"])

        wrong_settings = self._make_settings(secret="different-secret-that-is-32-chars!!")

        result = decode_access_token(token, wrong_settings)

        assert result is None

    def test_returns_none_for_non_access_token(self):
        """Returns None when typ is not 'access'."""
        settings = self._make_settings()

        # Create a refresh token (typ != "access")
        now = int(time.time())
        payload = {
            "iss": settings.jwt_issuer,
            "sub": "user-123",
            "roles": ["student"],
            "typ": "refresh",  # Wrong type
            "iat": now,
            "exp": now + 900,
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        result = decode_access_token(token, settings)

        assert result is None

    def test_returns_none_for_tampered_token(self):
        """Returns None for tampered/invalid tokens."""
        settings = self._make_settings()
        token = mint_access_token(settings, sub="user-123", roles=["student"])

        # Tamper with the token
        tampered = token[:-5] + "XXXXX"

        result = decode_access_token(tampered, settings)

        assert result is None

    def test_returns_none_for_empty_string(self):
        """Returns None for empty string token."""
        settings = self._make_settings()

        result = decode_access_token("", settings)

        assert result is None

    def test_returns_none_for_random_string(self):
        """Returns None for random non-JWT string."""
        settings = self._make_settings()

        result = decode_access_token("not-a-jwt-token", settings)

        assert result is None

    def test_requires_exp_claim(self):
        """Token without exp claim is rejected."""
        settings = self._make_settings()

        now = int(time.time())
        payload = {
            "iss": settings.jwt_issuer,
            "sub": "user-123",
            "roles": ["student"],
            "typ": "access",
            "iat": now,
            # Missing "exp"
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        result = decode_access_token(token, settings)

        assert result is None

    def test_requires_iss_claim(self):
        """Token without iss claim is rejected."""
        settings = self._make_settings()

        now = int(time.time())
        payload = {
            "sub": "user-123",
            "roles": ["student"],
            "typ": "access",
            "iat": now,
            "exp": now + 900,
            # Missing "iss"
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        result = decode_access_token(token, settings)

        assert result is None

    def test_requires_sub_claim(self):
        """Token without sub claim is rejected."""
        settings = self._make_settings()

        now = int(time.time())
        payload = {
            "iss": settings.jwt_issuer,
            "roles": ["student"],
            "typ": "access",
            "iat": now,
            "exp": now + 900,
            # Missing "sub"
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        result = decode_access_token(token, settings)

        assert result is None
