"""File extension inference utilities."""

import logging
import mimetypes
import os
from typing import IO, Optional, Union

try:
    import magic
except ImportError:
    magic = None  # type: ignore

from vellum.utils.files.constants import EXTENSION_OVERRIDES, MIME_TYPE_TO_EXTENSION

logger = logging.getLogger(__name__)


def ensure_filename_with_extension(
    filename: Optional[str], mime_type: str, contents: Optional[Union[bytes, IO[bytes]]] = None
) -> str:
    """
    Ensure the filename has an appropriate extension, infering one based on the provided MIME type if necessary.

    Args:
        filename: Optional filename provided by the user
        mime_type: The MIME type of the file (e.g., "application/pdf", "image/png"). This'll be used to infer the
            extension if the filename lacks one.
        contents: Optional file contents (bytes or file-like object) to use for MIME type detection via python-magic
            when the provided MIME type is generic or missing.

    Returns:
        A filename with an appropriate extension

    Examples:
        >>> ensure_filename_with_extension(None, "application/pdf")
        'file.pdf'
        >>> ensure_filename_with_extension("document", "application/pdf")
        'document.pdf'
        >>> ensure_filename_with_extension("document.pdf", "application/pdf")
        'document.pdf'
        >>> ensure_filename_with_extension("document.pdf", "image/jpeg")
        'document.pdf'  # Prioritizes existing extension
    """
    # Strip parameters from MIME type (e.g., "text/html; charset=utf-8" -> "text/html")
    mime_type = mime_type.split(";")[0].strip()

    # If no filename provided, start with "file"
    if not filename:
        base_name = "file"
        has_extension = False
    else:
        base_name = filename
        # Check if filename already has an extension
        _, ext = os.path.splitext(filename)
        has_extension = bool(ext)

    # If the provided filename already has an extension, keep it
    if filename and has_extension:
        return filename

    if mime_type == "application/octet-stream" and contents and magic:
        try:
            if isinstance(contents, bytes):
                sample = contents[:2048]
            else:
                original_position = contents.tell() if hasattr(contents, "tell") else None
                sample = contents.read(2048)
                if hasattr(contents, "seek") and original_position is not None:
                    contents.seek(original_position)

            detected_mime_type = magic.from_buffer(sample, mime=True)
            if detected_mime_type:
                # Strip any charset parameters from detected MIME type
                mime_type = detected_mime_type.split(";")[0].strip()
        except Exception:
            logger.exception("Failed to guess content type using python-magic")

    # Otherwise, infer extension from MIME type
    extension = mimetypes.guess_extension(mime_type)

    # Handle cases where mimetypes returns None or undesirable extensions
    if not extension:
        extension = MIME_TYPE_TO_EXTENSION.get(mime_type, ".bin")

    # Some MIME types have multiple possible extensions; prefer the most common ones
    extension = EXTENSION_OVERRIDES.get(extension, extension)

    return f"{base_name}{extension}"
