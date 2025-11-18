"""File upload utilities for uploading files to Vellum."""

import base64
from io import BytesIO
import logging
import re
from typing import Optional

import requests

from vellum.client import Vellum as VellumClient
from vellum.client.core.api_error import ApiError
from vellum.client.core.file import File
from vellum.utils.files.constants import BASE64_DATA_URL_PATTERN, URL_PATTERN, VELLUM_FILE_SRC_PATTERN
from vellum.utils.files.exceptions import FileNotFoundError, FileRetrievalError, InvalidFileSourceError
from vellum.utils.files.types import VellumFileTypes
from vellum.workflows.vellum_client import create_vellum_client

logger = logging.getLogger(__name__)


def upload_vellum_file(
    vellum_file: VellumFileTypes,
    *,
    filename: Optional[str] = None,
    vellum_client: Optional[VellumClient] = None,
) -> VellumFileTypes:
    """
    Upload a file to Vellum and return a new VellumFile with the uploaded source.

    This function takes any VellumFile object (with a src that could be a base64 data URL,
    HTTP/HTTPS URL, or existing vellum:uploaded-file: identifier), downloads its content,
    and uploads it to Vellum's storage.

    Args:
        vellum_file: A VellumDocument, VellumImage, VellumAudio, or VellumVideo instance
        filename: Optional filename to use when uploading. If not provided, the API will determine a default.
        vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

    Returns:
        VellumFileTypes: A new VellumFile of the same type with the vellum:uploaded-file:{id} source

    Raises:
        InvalidFileSourceError: If the file source format is invalid
        FileRetrievalError: If the file cannot be retrieved from its source
        FileNotFoundError: If the file is not found at its source

    Example:
        ```python
        from vellum import VellumDocument, VellumImage
        from vellum.utils.files import upload_vellum_file

        # Upload a document from a URL
        doc = VellumDocument(src="https://example.com/doc.pdf")
        uploaded_doc = upload_vellum_file(doc, filename="my_document.pdf")

        # Upload a base64-encoded image
        image = VellumImage(src="data:image/png;base64,iVBORw0KGgo...")
        uploaded_image = upload_vellum_file(image, filename="screenshot.png")
        ```
    """
    src = vellum_file.src

    # Case 1: Vellum Uploaded File (already uploaded, just return as-is)
    match = re.match(VELLUM_FILE_SRC_PATTERN, src, re.IGNORECASE)
    if match:
        vellum_uploaded_file_id = match.group(1)
        logger.info(
            "File already uploaded to Vellum, returning unchanged",
            extra={"vellum_uploaded_file_id": vellum_uploaded_file_id},
        )
        return vellum_file

    vellum_client = vellum_client or create_vellum_client()

    # Case 2: Base64 Data URL
    data_url_match = re.match(BASE64_DATA_URL_PATTERN, src)
    if data_url_match:
        mime_type = data_url_match.group(1) or "application/octet-stream"
        base64_content = data_url_match.group(3)
        decoded = base64.b64decode(base64_content)

        file_content: File = (filename, BytesIO(decoded), mime_type)

        try:
            uploaded_file = vellum_client.uploaded_files.create(file=file_content)
        except ApiError as e:
            raise FileRetrievalError(f"Failed to upload file to Vellum: {str(e)}") from e

        new_src = f"vellum:uploaded-file:{uploaded_file.id}"
        return _copy_with_new_src(vellum_file, new_src)

    # Case 3: Direct URL
    if not re.match(URL_PATTERN, src):
        raise InvalidFileSourceError(
            f"Invalid file source: {src}. "
            "Expected a base64 data URL (data:...;base64,...), "
            "a Vellum uploaded file ID (vellum:uploaded-file:...), "
            "or an HTTP/HTTPS URL."
        )

    file_url = src

    # Download from URL
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise FileNotFoundError(f"File not found at URL: {file_url}") from e
        raise FileRetrievalError(f"Failed to retrieve file from URL: {file_url}") from e
    except requests.RequestException as e:
        raise FileRetrievalError(f"Network error while retrieving file: {file_url}") from e

    # Read content and get content type
    content = response.content
    content_type = response.headers.get("content-type", "application/octet-stream")

    file_content = (filename, BytesIO(content), content_type)

    try:
        uploaded_file = vellum_client.uploaded_files.create(file=file_content)
    except ApiError as e:
        raise FileRetrievalError(f"Failed to upload file to Vellum: {str(e)}") from e

    new_src = f"vellum:uploaded-file:{uploaded_file.id}"
    return _copy_with_new_src(vellum_file, new_src)


def _copy_with_new_src(vellum_file: VellumFileTypes, new_src: str) -> VellumFileTypes:
    """Helper to create a copy of a VellumFile with an updated src."""
    # Use model_copy for Pydantic v2, copy for v1
    if hasattr(vellum_file, "model_copy"):
        return vellum_file.model_copy(update={"src": new_src})
    else:
        return vellum_file.copy(update={"src": new_src})
