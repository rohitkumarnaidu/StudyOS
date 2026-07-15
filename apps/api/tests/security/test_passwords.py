"""Tests for password hashing."""

from studyos_api.security.passwords import hash_password, verify_password


class TestPasswordHashing:
    def test_hash_password(self) -> None:
        hashed = hash_password("testpassword123")
        assert hashed is not None
        assert hashed != "testpassword123"
        assert "$argon2" in hashed

    def test_verify_password_correct(self) -> None:
        hashed = hash_password("testpassword123")
        assert verify_password("testpassword123", hashed) is True

    def test_verify_password_incorrect(self) -> None:
        hashed = hash_password("testpassword123")
        assert verify_password("wrongpassword", hashed) is False
