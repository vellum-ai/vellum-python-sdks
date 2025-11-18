from typing import Any, ContextManager, Iterator, Optional

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.utils.files.read import read_vellum_file
from vellum.utils.files.stream import stream_vellum_file
from vellum.utils.files.upload import upload_vellum_file


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
        Upload the file to Vellum and return a new instance with the uploaded source.

        This method takes the file (with a src that could be a base64 data URL,
        HTTP/HTTPS URL, or existing vellum:uploaded-file: identifier), downloads its content,
        and uploads it to Vellum's storage.

        Args:
            filename: Optional filename to use when uploading. If not provided, the API will determine a default.
            vellum_client: An optional Vellum client instance. If not provided, a default client will be created.

        Returns:
            A new instance with the vellum:uploaded-file:{id} source
        """
        return upload_vellum_file(self, filename=filename, vellum_client=vellum_client)
