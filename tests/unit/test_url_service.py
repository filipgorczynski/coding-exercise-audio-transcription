"""Tests for URL service functions."""

import pytest
from unittest.mock import patch, AsyncMock

from services.url_service import url_service


class TestUrlServiceDownload:
    """Test URL download functionality."""

    @pytest.mark.asyncio
    @patch("services.url_service.httpx.AsyncClient")
    async def test_download_follows_redirects(self, mock_client_class, temp_dir):
        """Test that downloads follow redirects."""
        mock_response = AsyncMock()
        mock_response.headers.get.return_value = "audio/mpeg"
        mock_response.content = b"data"
        mock_response.raise_for_status = AsyncMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = AsyncMock()
        mock_client_class.return_value = mock_client

        await url_service.download_from_url("https://example.com/audio.mp3", temp_dir)

        # Verify follow_redirects=True was passed
        call_kwargs = mock_client.get.call_args.kwargs
        assert call_kwargs.get("follow_redirects") is True
