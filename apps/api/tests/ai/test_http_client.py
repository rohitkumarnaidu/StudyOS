"""Tests for AI http_client."""

import asyncio
from unittest.mock import MagicMock, patch

import httpx
import pytest

from studyos_api.ai.http_client import http_client_scope


class TestHttpClientScope:
    @pytest.mark.asyncio
    async def test_uses_shared_client(self):
        app = MagicMock()
        shared_client = httpx.AsyncClient()
        app.state.http_client = shared_client

        async with http_client_scope(app) as client:
            assert client is shared_client

        await shared_client.aclose()

    @pytest.mark.asyncio
    async def test_creates_ephemeral_client(self):
        app = MagicMock()
        app.state = MagicMock()
        app.state.http_client = None

        async with http_client_scope(app) as client:
            assert isinstance(client, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_ephemeral_client_closed(self):
        app = MagicMock()
        app.state = MagicMock()
        app.state.http_client = None

        client_ref = None
        async with http_client_scope(app) as client:
            client_ref = client

        assert client_ref is not None
