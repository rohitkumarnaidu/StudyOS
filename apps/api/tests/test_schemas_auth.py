"""Tests for schemas — auth, common, examples."""

import pytest
from pydantic import ValidationError

from studyos_api.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


@pytest.mark.unit
class TestLoginRequest:
    """Test LoginRequest schema validation."""

    def test_valid_login_request(self):
        """Accepts valid email and password."""
        req = LoginRequest(email="user@example.com", password="password123")
        assert req.email == "user@example.com"
        assert req.password == "password123"

    def test_email_min_length(self):
        """Email must be at least 3 characters."""
        with pytest.raises(ValidationError):
            LoginRequest(email="ab", password="password123")

    def test_email_max_length(self):
        """Email must be at most 320 characters."""
        long_email = "a" * 321 + "@example.com"
        with pytest.raises(ValidationError):
            LoginRequest(email=long_email, password="password123")

    def test_password_min_length(self):
        """Password must be at least 1 character."""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com", password="")

    def test_password_max_length(self):
        """Password must be at most 256 characters."""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com", password="a" * 257)


@pytest.mark.unit
class TestRegisterRequest:
    """Test RegisterRequest schema validation."""

    def test_valid_register_request(self):
        """Accepts valid email, password, and display_name."""
        req = RegisterRequest(
            email="newuser@example.com",
            password="SecurePass123!",
            display_name="New User",
        )
        assert req.email == "newuser@example.com"
        assert req.password == "SecurePass123!"
        assert req.display_name == "New User"

    def test_requires_valid_email(self):
        """Email must be a valid EmailStr."""
        with pytest.raises(ValidationError):
            RegisterRequest(email="not-an-email", password="SecurePass123!", display_name="Test")

    def test_password_min_length_8(self):
        """Password must be at least 8 characters."""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="Short1!",
                display_name="Test",
            )

    def test_password_max_length(self):
        """Password must be at most 256 characters."""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="a" * 257,
                display_name="Test",
            )

    def test_display_name_min_length(self):
        """Display name must be at least 1 character."""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="SecurePass123!",
                display_name="",
            )

    def test_display_name_max_length(self):
        """Display name must be at most 100 characters."""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="SecurePass123!",
                display_name="a" * 101,
            )


@pytest.mark.unit
class TestRefreshRequest:
    """Test RefreshRequest schema validation."""

    def test_valid_refresh_request(self):
        """Accepts valid refresh token."""
        req = RefreshRequest(refresh_token="rt_abc123xyz")
        assert req.refresh_token == "rt_abc123xyz"

    def test_refresh_token_min_length(self):
        """Refresh token must be at least 8 characters."""
        with pytest.raises(ValidationError):
            RefreshRequest(refresh_token="short")

    def test_refresh_token_max_length(self):
        """Refresh token must be at most 4096 characters."""
        with pytest.raises(ValidationError):
            RefreshRequest(refresh_token="a" * 4097)


@pytest.mark.unit
class TestLogoutRequest:
    """Test LogoutRequest schema validation."""

    def test_valid_logout_request_with_token(self):
        """Accepts logout with refresh token."""
        req = LogoutRequest(refresh_token="rt_abc123")
        assert req.refresh_token == "rt_abc123"

    def test_valid_logout_request_without_token(self):
        """Accepts logout without refresh token (None is valid)."""
        req = LogoutRequest()
        assert req.refresh_token is None

    def test_refresh_token_max_length(self):
        """Refresh token must be at most 4096 characters."""
        with pytest.raises(ValidationError):
            LogoutRequest(refresh_token="a" * 4097)


@pytest.mark.unit
class TestTokenResponse:
    """Test TokenResponse schema."""

    def test_valid_token_response(self):
        """Creates valid token response."""
        resp = TokenResponse(
            access_token="at_abc123",
            refresh_token="rt_xyz789",
            expires_in=900,
        )
        assert resp.access_token == "at_abc123"
        assert resp.refresh_token == "rt_xyz789"
        assert resp.token_type == "Bearer"
        assert resp.expires_in == 900

    def test_default_token_type(self):
        """token_type defaults to 'Bearer'."""
        resp = TokenResponse(
            access_token="at_abc123",
            refresh_token="rt_xyz789",
            expires_in=900,
        )
        assert resp.token_type == "Bearer"

    def test_token_type_must_be_bearer(self):
        """token_type must be 'Bearer'."""
        with pytest.raises(ValidationError):
            TokenResponse(
                access_token="at_abc123",
                refresh_token="rt_xyz789",
                expires_in=900,
                token_type="Basic",
            )


@pytest.mark.unit
class TestUserResponse:
    """Test UserResponse schema."""

    def test_valid_user_response(self):
        """Creates valid user response."""
        resp = UserResponse(
            sub="user-123",
            email="user@example.com",
            display_name="Test User",
        )
        assert resp.sub == "user-123"
        assert resp.email == "user@example.com"
        assert resp.display_name == "Test User"
        assert resp.app_role == "student"

    def test_default_app_role(self):
        """app_role defaults to 'student'."""
        resp = UserResponse(
            sub="user-123",
            email="user@example.com",
            display_name="Test User",
        )
        assert resp.app_role == "student"

    def test_custom_app_role(self):
        """app_role can be set to other values."""
        resp = UserResponse(
            sub="user-123",
            email="user@example.com",
            display_name="Test User",
            app_role="teacher",
        )
        assert resp.app_role == "teacher"
