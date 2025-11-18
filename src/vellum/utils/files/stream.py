"""Streaming utilities for reading Vellum files."""

import base64
from contextlib import contextmanager
from io import BytesIO
import re
from typing import TYPE_CHECKING, Generator, Iterator, Optional

import requests

from vellum.client.core.api_error import ApiError
from vellum.utils.files.constants import BASE64_DATA_URL_PATTERN, URL_PATTERN, VELLUM_FILE_SRC_PATTERN
from vellum.utils.files.exceptions import FileNotFoundError, FileRetrievalError, InvalidFileSourceError
from vellum.utils.files.types import VellumFileTypes

if TYPE_CHECKING:
    from vellum.client import Vellum as VellumClient


@contextmanager
def stream_vellum_file(
    vellum_file: VellumFileTypes,
    *,
    chunk_size: int = 8192,
    vellum_client: Optional["VellumClient"] = None,
) -> Generator[Iterator[bytes], None, None]:
    """
    Stream the file content in chunks using a context manager.

    This is the recommended way to read large files, as it avoids loading
    the entire file into memory at once.

    Args:
        vellum_file: A VellumDocument, VellumImage, VellumAudio, or VellumVideo instance
        chunk_size: Size of chunks to yield in bytes (default 8KB)
        vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

    Yields:
        Iterator[bytes]: Chunks of file content

    Example:
        ```python
        from vellum import VellumVideo
        from vellum.utils.files import stream_vellum_file

        # Stream a large video file
        video = VellumVideo(src="https://example.com/video.mp4")
        with stream_vellum_file(video, chunk_size=10*1024*1024) as chunks:  # 10MB chunks
            with open('output.mp4', 'wb') as f:
                for chunk in chunks:
                    f.write(chunk)

        # Calculate hash without loading entire file
        import hashlib
        hasher = hashlib.sha256()
        with stream_vellum_file(vellum_file) as chunks:
            for chunk in chunks:
                hasher.update(chunk)
        hash_value = hasher.hexdigest()
        ```
    """
    src = vellum_file.src

    # Case 1: Base64 Data URL
    # Note: Base64 content is already in memory, but we still provide
    # a streaming interface for consistency
    data_url_match = re.match(BASE64_DATA_URL_PATTERN, src)
    if data_url_match:
        base64_content = data_url_match.group(3)
        decoded = base64.b64decode(base64_content)
        stream = BytesIO(decoded)
        try:
            yield _chunk_iterator(stream, chunk_size)
        finally:
            stream.close()
        return

    file_url: str

    # Case 2: Vellum Uploaded File
    match = re.match(VELLUM_FILE_SRC_PATTERN, src, re.IGNORECASE)
    if match:
        vellum_uploaded_file_id = match.group(1)
        if vellum_client is None:
            from vellum.utils.vellum_client import create_vellum_client

            vellum_client = create_vellum_client()

        try:
            uploaded_file = vellum_client.uploaded_files.retrieve(vellum_uploaded_file_id)
        except ApiError as e:
            if e.status_code == 404:
                raise FileNotFoundError(f"Uploaded file not found: {vellum_uploaded_file_id}") from e
            raise FileRetrievalError(f"Failed to retrieve uploaded file: {vellum_uploaded_file_id}") from e

        if not uploaded_file.file_url:
            raise FileRetrievalError(f"Uploaded file has no accessible URL: {vellum_uploaded_file_id}")

        file_url = uploaded_file.file_url

    # Case 3: Direct URL
    elif re.match(URL_PATTERN, src):
        file_url = src
    else:
        raise InvalidFileSourceError(
            f"Invalid file source: {src}. "
            "Expected a base64 data URL (data:...;base64,...), "
            "a Vellum uploaded file ID (vellum:uploaded-file:...), "
            "or an HTTP/HTTPS URL."
        )

    # Stream from URL
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise FileNotFoundError(f"File not found at URL: {file_url}") from e
        raise FileRetrievalError(f"Failed to retrieve file from URL: {file_url}") from e
    except requests.RequestException as e:
        raise FileRetrievalError(f"Network error while retrieving file: {file_url}") from e

    try:
        yield response.iter_content(chunk_size=chunk_size)
    finally:
        response.close()


def _chunk_iterator(stream: BytesIO, chunk_size: int) -> Iterator[bytes]:
    """Helper to read a BytesIO stream in chunks."""
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        yield chunk
