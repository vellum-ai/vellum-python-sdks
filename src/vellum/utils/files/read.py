"""Convenience utilities for reading Vellum files."""

from typing import TYPE_CHECKING, Optional

from vellum.utils.files.stream import stream_vellum_file
from vellum.utils.files.types import VellumFileTypes

if TYPE_CHECKING:
    from vellum.client import Vellum as VellumClient


def read_vellum_file(vellum_file: VellumFileTypes, *, vellum_client: Optional["VellumClient"] = None) -> bytes:
    """
    Convenience function that reads the entire file content into memory.

    This function is implemented using stream_vellum_file() under the hood.
    For large files (e.g., videos, large datasets), consider using
    stream_vellum_file() directly to avoid memory issues.

    Args:
        vellum_file: A VellumDocument, VellumImage, VellumAudio, or VellumVideo instance
        vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

    Returns:
        bytes: The complete file content

    Example:
        ```python
        from vellum import VellumDocument
        from vellum.utils.files import read_vellum_file

        document = VellumDocument(src="data:text/plain;base64,SGVsbG8gV29ybGQ=")
        content = read_vellum_file(document)
        print(content.decode('utf-8'))  # "Hello World"
        ```
    """
    chunks = []
    with stream_vellum_file(vellum_file, vellum_client=vellum_client) as chunk_iter:
        for chunk in chunk_iter:
            chunks.append(chunk)
    return b"".join(chunks)
