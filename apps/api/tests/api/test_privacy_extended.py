"""Extended tests for privacy endpoints — service-level tests."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from studyos_api.api.v1.routes.privacy import delete_account, export_user_data, get_db_pool


class TestPrivacyExportService:
    def test_get_db_pool(self):
        request = MagicMock()
        request.app.state.db_pool = MagicMock()
        assert get_db_pool(request) is request.app.state.db_pool

    def test_get_db_pool_none(self):
        request = MagicMock()
        request.app.state.db_pool = None
        assert get_db_pool(request) is None

    @pytest.mark.asyncio
    async def test_export_no_pool_raises_503(self):
        current_user = {"sub": str(uuid4())}
        request = MagicMock()

        with pytest.raises(Exception) as exc_info:
            await export_user_data(request, current_user, pool=None)

        assert exc_info.value.status_code == 503


class TestPrivacyDeleteService:
    @pytest.mark.asyncio
    async def test_delete_no_pool_raises_503(self):
        current_user = {"sub": str(uuid4())}
        request = MagicMock()

        with pytest.raises(Exception) as exc_info:
            await delete_account(request, current_user, pool=None)

        assert exc_info.value.status_code == 503
