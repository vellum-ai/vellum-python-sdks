"""File extension inference utilities."""

import mimetypes
import os
from typing import Optional

from vellum.utils.files.constants import EXTENSION_OVERRIDES, MIME_TYPE_TO_EXTENSION


def ensure_filename_with_extension(filename: Optional[str], mime_type: str) -> str:
    """
    Ensure the filename has an appropriate extension, infering one based on the provided MIME type if necessary.

    Args:
        filename: Optional filename provided by the user
        mime_type: The MIME type of the file (e.g., "application/pdf", "image/png"). This'll be used to infer the
            extension if the filename lacks one.

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

    # Otherwise, infer extension from MIME type
    extension = mimetypes.guess_extension(mime_type)

    # Handle cases where mimetypes returns None or undesirable extensions
    if not extension:
        extension = MIME_TYPE_TO_EXTENSION.get(mime_type, ".bin")

    # Some MIME types have multiple possible extensions; prefer the most common ones
    extension = EXTENSION_OVERRIDES.get(extension, extension)

    return f"{base_name}{extension}"
