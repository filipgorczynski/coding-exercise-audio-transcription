"""URL download service for YouTube and media URLs."""

import os
from typing import Tuple

import httpx
from fastapi import HTTPException, status


class UrlService:
    """Handle downloading from URLs."""

    @staticmethod
    async def download_from_url(url: str, output_dir: str) -> Tuple[str, str]:
        """
        Download media from URL.
        Returns: (file_path, file_type)
        """
        try:
            return await UrlService._download_direct(url, output_dir)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to download from URL: {str(e)}",
            )

    # TODO(fgorczynski): add unique session id (uuid) from parent
    @staticmethod
    async def _download_direct(url: str, output_dir: str) -> Tuple[str, str]:
        """Download media from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")

            filename = url.split("/")[-1] or "downloaded_file"
            if "?" in filename:
                filename = filename.split("?")[0]

            file_path = os.path.join(output_dir, filename)

            with open(file_path, "wb") as f:
                f.write(response.content)

            return file_path, content_type


url_service = UrlService()
