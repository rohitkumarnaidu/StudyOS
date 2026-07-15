"""Tests for deps/auth.py — authentication dependency injection."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status

from studyos_api.deps.auth import (
    _parse_bearer,
    get_auth_service,
    get_current_user,
    get_current_user_optional,
)
from studyos_api.types.principal import User


@pytest.mark.unit
class TestParseBearer:
    """Test _parse_bearer helper function."""

    def test_parses_valid_bearer_token(self):
        """Extracts token from 'Bearer <token>' header."""
        result = _parse_bearer("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test")
        assert result == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"

    def test_case_insensitive_bearer(self):
        """Accepts 'bearer' in any case."""
        assert _parse_bearer("bearer token123") == "token123"
        assert _parse_bearer("BEARER token123") == "token123"
        assert _parse_bearer("BeArEr token123") == "token123"

    def test_returns_none_for_none_input(self):
        """Returns None when authorization is None."""
        assert _parse_bearer(None) is None

    def test_returns_none_for_empty_string(self):
        """Returns None when authorization is empty."""
        assert _parse_bearer("") is None

    def test_returns_none_for_non_bearer_prefix(self):
        """Returns None for non-Bearer auth schemes."""
        assert _parse_bearer("Basic dXNlcjpwYXNz") is None
        assert _parse_bearer("Token abc123") is None
        assert _parse_bearer("ApiKey xyz") is None

    def test_returns_none_for_bearer_without_token(self):
        """Returns None when 'Bearer' has no token after it."""
        assert _parse_bearer("Bearer ") is None
        assert _parse_bearer("Bearer") is None

    def test_strips_whitespace_from_token(self):
        """Strips leading/trailing whitespace from extracted token."""
        result = _parse_bearer("Bearer  my-token  ")
        assert result == "my-token"


@pytest.mark.unit
class TestGetAuthService:
    """Test get_auth_service dependency."""

    def test_returns_auth_service_instance(self):
        """Returns an AuthService instance."""
        from studyos_api.services.auth_service import AuthService
        service = get_auth_service()
        assert isinstance(service, AuthService)


@pytest.mark.unit
class TestGetCurrentUserOptional:
    """Test get_current_user_optional dependency."""

    def test_returns_user_with_valid_token(self):
        """Returns User when valid Bearer token provided."""
        mock_user = User(user_id="user-123", email="test@example.com", roles=["student"])
        mock_auth = MagicMock()
        mock_auth.resolve_optional_user.return_value = mock_user

        result = get_current_user_optional(mock_auth, "Bearer valid-token")

        assert result == mock_user
        mock_auth.resolve_optional_user.assert_called_once_with("valid-token")

    def test_returns_none_without_authorization(self):
        """Returns None when no Authorization header."""
        mock_auth = MagicMock()
        mock_auth.resolve_optional_user.return_value = None

        result = get_current_user_optional(mock_auth, None)

        assert result is None

    def test_returns_none_with_invalid_token(self):
        """Returns None when token is invalid."""
        mock_auth = MagicMock()
        mock_auth.resolve_optional_user.return_value = None

        result = get_current_user_optional(mock_auth, "Bearer invalid-token")

        assert result is None

    def test_returns_none_with_non_bearer_auth(self):
        """Returns None for non-Bearer auth schemes."""
        mock_auth = MagicMock()
        mock_auth.resolve_optional_user.return_value = None

        result = get_current_user_optional(mock_auth, "Basic dXNlcjpwYXNz")

        assert result is None


@pytest.mark.unit
class TestGetCurrentUser:
    """Test get_current_user dependency (raises 401 if no user)."""

    def test_returns_user_when_present(self):
        """Returns User when user is resolved."""
        mock_user = User(user_id="user-123", email="test@example.com", roles=["student"])

        result = get_current_user(mock_user)

        assert result == mock_user

    def test_raises_401_when_user_is_none(self):
        """Raises HTTPException 401 when user is None."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Missing or invalid credentials"
