"""File upload utilities for uploading files to Vellum."""

import logging
import re
from typing import TYPE_CHECKING, Optional

from vellum.client.core.api_error import ApiError
from vellum.utils.files.constants import VELLUM_FILE_SRC_PATTERN
from vellum.utils.files.exceptions import FileRetrievalError, InvalidFileSourceError
from vellum.utils.files.types import VellumFileTypes
from vellum.utils.files.upload import upload_vellum_file

if TYPE_CHECKING:
    from vellum.client import Vellum as VellumClient

logger = logging.getLogger(__name__)


def get_signed_url(
    vellum_file: VellumFileTypes,
    *,
    expiry_seconds: int = 7 * 24 * 60 * 60,  # 7 days
    vellum_client: Optional["VellumClient"] = None,
) -> str:
    """
    Retrieved a signed url for a file that's been uploaded to Vellum

    This function takes any VellumFile object (with a src that could be a base64 data URL,
    HTTP/HTTPS URL, or existing vellum:uploaded-file: identifier), uploads it to Vellum (if not already uploaded),
    and returns a signed url for accessing the file.

    Args:
        vellum_file: A VellumDocument, VellumImage, VellumAudio, or VellumVideo instance
        expiry_seconds: The number of seconds until the signed URL expires. Defaults to 7 days.
        vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

    Returns:
        str: A signed URL for accessing the uploaded file
    """

    # Upload the file to Vellum if it isn't already
    uploaded_file = upload_vellum_file(vellum_file, vellum_client=vellum_client)

    # Parse out its reference ID
    vellum_uploaded_file_id: Optional[str] = None
    src = uploaded_file.src
    match = re.match(VELLUM_FILE_SRC_PATTERN, src, re.IGNORECASE)
    if match:
        vellum_uploaded_file_id = match.group(1)

    if not vellum_uploaded_file_id:
        raise InvalidFileSourceError("Failed to determine id of uploaded file.")

    if vellum_client is None:
        from vellum.utils.vellum_client import create_vellum_client

        vellum_client = create_vellum_client()

    # Fetch the signed URL for this file from Vellum
    try:
        vellum_uploaded_file = vellum_client.uploaded_files.retrieve(
            vellum_uploaded_file_id, expiry_seconds=expiry_seconds
        )
    except ApiError as e:
        raise FileRetrievalError("Failed to retrieve file from Vellum") from e

    signed_url = vellum_uploaded_file.file_url
    if not signed_url:
        raise FileRetrievalError("Failed to retrieve signed URL for uploaded file.")

    return signed_url
