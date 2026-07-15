"""Tests for HTTP utilities."""

from unittest.mock import MagicMock

from studyos_api.utils.http import client_ip


class TestClientIp:
    def test_with_client(self) -> None:
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        assert client_ip(mock_request) == "127.0.0.1"

    def test_without_client(self) -> None:
        mock_request = MagicMock()
        mock_request.client = None
        assert client_ip(mock_request) == "unknown"
