"""Tests for services/me_service.py — identity service."""

import pytest

from studyos_api.services.me_service import MeService


@pytest.mark.unit
class TestMeService:
    """Test MeService business logic."""

    def test_build_me_payload_for_authenticated_user(self):
        """Returns authenticated=True with user details."""
        service = MeService()
        user = {
            "sub": "user-123",
            "roles": ["student"],
            "email": "test@example.com",
        }

        payload = service.build_me_payload(user)

        assert payload.authenticated is True
        assert payload.user is not None
        assert payload.user.sub == "user-123"
        assert payload.user.roles == ["student"]

    def test_build_me_payload_for_anonymous_user(self):
        """Returns authenticated=False when user is None."""
        service = MeService()

        payload = service.build_me_payload(None)

        assert payload.authenticated is False
        assert payload.user is None

    def test_build_me_payload_copies_roles(self):
        """Roles are copied (not referenced) to prevent mutation."""
        service = MeService()
        user = {"sub": "user-456", "roles": ["student", "teacher"]}

        payload = service.build_me_payload(user)

        assert payload.user.roles == ["student", "teacher"]
        # Mutating original shouldn't affect payload
        user["roles"].append("admin")
        assert payload.user.roles == ["student", "teacher"]

    def test_build_me_payload_with_multiple_roles(self):
        """Handles users with multiple roles."""
        service = MeService()
        user = {"sub": "user-789", "roles": ["student", "teacher", "admin"]}

        payload = service.build_me_payload(user)

        assert payload.authenticated is True
        assert len(payload.user.roles) == 3
        assert "student" in payload.user.roles
        assert "teacher" in payload.user.roles
        assert "admin" in payload.user.roles
