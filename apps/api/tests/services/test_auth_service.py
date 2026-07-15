"""Tests for AuthService."""

from unittest.mock import MagicMock, patch

import pytest

from studyos_api.services.auth_service import AuthService


class TestAuthServiceResolveOptionalUser:
    def test_none_token(self):
        svc = AuthService()
        assert svc.resolve_optional_user(None) is None

    def test_empty_token(self):
        svc = AuthService()
        assert svc.resolve_optional_user("") is None

    def test_valid_jwt_token(self):
        svc = AuthService()
        fake_claims = {"sub": "user-123", "roles": ["student", "admin"]}

        with patch("studyos_api.services.auth_service.decode_access_token", return_value=fake_claims):
            with patch("studyos_api.services.auth_service.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(allow_legacy_demo_bearer=False)
                user = svc.resolve_optional_user("valid.jwt.token")

        assert user is not None
        assert user["sub"] == "user-123"
        assert user["roles"] == ["student", "admin"]

    def test_valid_jwt_token_no_roles(self):
        svc = AuthService()
        fake_claims = {"sub": "user-123"}

        with patch("studyos_api.services.auth_service.decode_access_token", return_value=fake_claims):
            with patch("studyos_api.services.auth_service.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(allow_legacy_demo_bearer=False)
                user = svc.resolve_optional_user("valid.jwt.token")

        assert user is not None
        assert user["sub"] == "user-123"
        assert user["roles"] == []

    def test_valid_jwt_token_roles_not_list(self):
        svc = AuthService()
        fake_claims = {"sub": "user-123", "roles": "student"}

        with patch("studyos_api.services.auth_service.decode_access_token", return_value=fake_claims):
            with patch("studyos_api.services.auth_service.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(allow_legacy_demo_bearer=False)
                user = svc.resolve_optional_user("valid.jwt.token")

        assert user is not None
        assert user["roles"] == []

    def test_invalid_token_demo_disabled(self):
        svc = AuthService()

        with patch("studyos_api.services.auth_service.decode_access_token", return_value=None):
            with patch("studyos_api.services.auth_service.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(allow_legacy_demo_bearer=False)
                user = svc.resolve_optional_user("invalid.token")

        assert user is None

    def test_demo_bearer_student(self):
        svc = AuthService()

        with patch("studyos_api.services.auth_service.decode_access_token", return_value=None):
            with patch("studyos_api.services.auth_service.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(allow_legacy_demo_bearer=True)
                user = svc.resolve_optional_user("demo")

        assert user is not None
        assert user["sub"] == "demo-user"
        assert user["roles"] == ["student"]

    def test_demo_bearer_admin(self):
        svc = AuthService()

        with patch("studyos_api.services.auth_service.decode_access_token", return_value=None):
            with patch("studyos_api.services.auth_service.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(allow_legacy_demo_bearer=True)
                user = svc.resolve_optional_user("admin")

        assert user is not None
        assert user["sub"] == "admin-user"
        assert user["roles"] == ["admin"]

    def test_demo_bearer_unknown(self):
        svc = AuthService()

        with patch("studyos_api.services.auth_service.decode_access_token", return_value=None):
            with patch("studyos_api.services.auth_service.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(allow_legacy_demo_bearer=True)
                user = svc.resolve_optional_user("unknown")

        assert user is None

    def test_valid_token_takes_precedence_over_demo(self):
        svc = AuthService()
        fake_claims = {"sub": "real-user", "roles": ["student"]}

        with patch("studyos_api.services.auth_service.decode_access_token", return_value=fake_claims):
            with patch("studyos_api.services.auth_service.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(allow_legacy_demo_bearer=True)
                user = svc.resolve_optional_user("demo")

        assert user is not None
        assert user["sub"] == "real-user"
