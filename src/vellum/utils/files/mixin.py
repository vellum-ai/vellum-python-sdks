import base64
import binascii
import re
from typing import Any, ContextManager, Iterator, Optional

from pydantic import field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.utils.files.constants import BASE64_DATA_URL_PATTERN
from vellum.utils.files.exceptions import InvalidFileSourceError
from vellum.utils.files.read import read_vellum_file
from vellum.utils.files.stream import stream_vellum_file
from vellum.utils.files.upload import upload_vellum_file
from vellum.utils.files.urls import get_signed_url


class VellumFileMixin(UniversalBaseModel):
    """Mixin class that provides stream, read, and upload methods for Vellum file types.

    This class extends UniversalBaseModel, so file types can inherit from this
    instead of both UniversalBaseModel and VellumFileMixin.
    """

    def stream(
        self: Any,
        *,
        chunk_size: int = 8192,
        vellum_client: Optional[Any] = None,
    ) -> ContextManager[Iterator[bytes]]:
        """
        Stream the file content in chunks using a context manager.

        This is the recommended way to read large files, as it avoids loading
        the entire file into memory at once.

        Args:
            chunk_size: Size of chunks to yield in bytes (default 8KB)
            vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

        Returns:
            A context manager that yields an iterator of file content chunks.

        Example:
            ```python
            with file.stream() as chunks:
                for chunk in chunks:
                    process(chunk)
            ```
        """
        return stream_vellum_file(self, chunk_size=chunk_size, vellum_client=vellum_client)

    def read(
        self: Any,
        *,
        vellum_client: Optional[Any] = None,
    ) -> bytes:
        """
        Read the entire file content into memory.

        For large files (e.g., videos, large datasets), consider using
        stream() directly to avoid memory issues.

        Args:
            vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

        Returns:
            bytes: The complete file content
        """
        return read_vellum_file(self, vellum_client=vellum_client)

    def upload(
        self: Any,
        *,
        filename: Optional[str] = None,
        vellum_client: Optional[Any] = None,
    ) -> Any:
        """
        Upload a file to Vellum and return a new VellumFile with the uploaded source.

        This function takes any VellumFile object (with a src that could be a base64 data URL,
        HTTP/HTTPS URL, or existing vellum:uploaded-file: identifier), downloads its content,
        and uploads it to Vellum's storage.

        Args:
            vellum_file: A VellumDocument, VellumImage, VellumAudio, or VellumVideo instance
            filename: Optional filename to use when uploading. If not provided, defaults to "file"
                     with an appropriate extension inferred from the MIME type. If provided without
                     an extension, the extension will be automatically added based on the MIME type.
            vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

        Returns:
            A new instance with the vellum:uploaded-file:{id} source
        """
        return upload_vellum_file(self, filename=filename, vellum_client=vellum_client)

    def get_signed_url(
        self: Any,
        *,
        expiry_seconds: int = 7 * 24 * 60 * 60,  # 7 days
        vellum_client: Optional[Any] = None,
    ) -> str:
        """
        Retrieved a signed url for a file that's been uploaded to Vellum

        This function takes any VellumFile object (with a src that could be a base64 data URL,
        HTTP/HTTPS URL, or existing vellum:uploaded-file: identifier), uploads it to Vellum (if not already uploaded),
        and returns a signed url for accessing the file.

        Args:
            expiry_seconds: The number of seconds until the signed URL expires. Defaults to 7 days.
            vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

        Returns:
            str: A signed URL for accessing the uploaded file
        """
        return get_signed_url(self, expiry_seconds=expiry_seconds, vellum_client=vellum_client)

    @field_serializer("src", check_fields=False)
    @classmethod
    def validate_src_on_serialize(cls, src: str) -> str:
        """Validate the src field during serialization.

        For PDF base64 data URLs, this validates that the base64 content is properly encoded.
        """
        data_url_match = re.match(BASE64_DATA_URL_PATTERN, src)
        if data_url_match:
            mime_type = data_url_match.group(1) or ""
            if mime_type == "application/pdf":
                base64_content = data_url_match.group(3)
                try:
                    base64.b64decode(base64_content, validate=True)
                except binascii.Error as e:
                    raise InvalidFileSourceError(f"Invalid base64 encoding in PDF data URL: {e}") from e

        return src
