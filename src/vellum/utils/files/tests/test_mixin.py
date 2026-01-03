import pytest
import base64
from unittest.mock import Mock, patch

from pydantic_core import PydanticSerializationError

from vellum.utils.files import VellumFileMixin

# Sample content for testing
SAMPLE_TEXT_CONTENT = b"Hello, this is a test document!"


class TestDocument(VellumFileMixin):
    """Test class that demonstrates how VellumFileMixin is used in postprocess.

    This mirrors the pattern used in postprocess.ts where file types inherit from
    VellumFileMixin (which extends UniversalBaseModel), replacing UniversalBaseModel.
    """

    src: str


def test_vellum_file_mixin_stream_method():
    """Test that VellumFileMixin.stream() method works."""

    # GIVEN a test document with base64 content using the mixin (like postprocess does)
    content = b"Hello, this is a test document!"
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    test_file = TestDocument(src=src)

    # WHEN streaming using the mixin's .stream() method
    chunks = []
    with test_file.stream() as chunk_iter:
        for chunk in chunk_iter:
            chunks.append(chunk)

    # THEN the content should match
    result = b"".join(chunks)
    assert result == content


def test_vellum_file_mixin_stream_method_with_custom_chunk_size():
    """Test that VellumFileMixin.stream() respects custom chunk_size parameter."""

    # GIVEN a test document with content using the mixin (like postprocess does)
    content = b"This is a longer document that will be split into multiple chunks."
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    test_file = TestDocument(src=src)

    # WHEN streaming with a small chunk size using the mixin
    chunk_size = 10
    chunks = []
    with test_file.stream(chunk_size=chunk_size) as chunk_iter:
        for chunk in chunk_iter:
            chunks.append(chunk)
            # Each chunk should be <= chunk_size (last chunk may be smaller)
            assert len(chunk) <= chunk_size

    # THEN the content should match when reassembled
    result = b"".join(chunks)
    assert result == content
    # AND we should have multiple chunks for content larger than chunk_size
    assert len(chunks) > 1


def test_vellum_file_mixin_stream_method_from_url():
    """Test that VellumFileMixin.stream() method works for files from URLs."""

    # GIVEN a test document with a URL source using the mixin (like postprocess does)
    content = b"URL fetched content that will be streamed"
    url = "https://example.com/file.dat"
    test_file = TestDocument(src=url)

    # WHEN streaming using the mixin's .stream() method
    with patch("vellum.utils.files.stream.requests.get") as mock_get:
        mock_response = Mock()
        # Simulate streaming response with iter_content
        mock_response.iter_content = Mock(return_value=iter([content[:20], content[20:]]))
        mock_response.raise_for_status = Mock()
        mock_response.close = Mock()
        mock_get.return_value = mock_response

        chunks = []
        with test_file.stream() as chunk_iter:
            for chunk in chunk_iter:
                chunks.append(chunk)

        result = b"".join(chunks)
        assert result == content
        mock_get.assert_called_once_with(url, stream=True)
        mock_response.raise_for_status.assert_called_once()
        mock_response.close.assert_called_once()


def test_vellum_file_mixin_read_method():
    """Test that VellumFileMixin.read() method works."""

    # GIVEN a test document with base64 content using the mixin (like postprocess does)
    content = b"Hello, this is a test document!"
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    test_file = TestDocument(src=src)

    # WHEN reading using the mixin's .read() method
    result = test_file.read()

    # THEN the content should match
    assert result == content


def test_vellum_file_mixin_upload_method():
    """Test that VellumFileMixin.upload() method works."""

    # GIVEN a test document with base64 content using the mixin (like postprocess does)
    content = b"Hello, this is a test document!"
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    test_file = TestDocument(src=src)
    uploaded_file_id = "12345678-1234-1234-1234-123456789abc"

    # WHEN uploading using the mixin's .upload() method
    with patch("vellum.utils.vellum_client.create_vellum_client") as mock_create_client:
        mock_client = Mock()
        mock_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)
        mock_create_client.return_value = mock_client

        result = test_file.upload()

        # THEN the file should be uploaded and return a new instance with uploaded source
        assert result.src == f"vellum:uploaded-file:{uploaded_file_id}"
        assert isinstance(result, TestDocument)
        mock_client.uploaded_files.create.assert_called_once()


def test_vellum_file_mixin_get_signed_url_method():
    """Test that VellumFileMixin.get_signed_url() method works."""

    # GIVEN a test document with base64 content using the mixin (like postprocess does)
    content = b"Hello, this is a test document!"
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    test_file = TestDocument(src=src)
    uploaded_file_id = "12345678-1234-1234-1234-123456789abc"
    signed_url = "https://storage.vellum.ai/files/signed?token=abc123"

    # WHEN getting the signed URL using the mixin's .get_signed_url() method
    with patch("vellum.utils.vellum_client.create_vellum_client") as mock_create_client:
        mock_client = Mock()
        mock_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)
        mock_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)
        mock_create_client.return_value = mock_client

        result = test_file.get_signed_url()

        # THEN the file should be uploaded and signed URL returned
        assert result == signed_url
        mock_client.uploaded_files.create.assert_called_once()
        mock_client.uploaded_files.retrieve.assert_called_once_with(uploaded_file_id, expiry_seconds=604800)


def test_vellum_file_mixin_get_signed_url_method_with_custom_client():
    """Test that VellumFileMixin.get_signed_url() respects custom vellum_client parameter."""

    # GIVEN a test document with base64 content using the mixin (like postprocess does)
    content = b"Hello, this is a test document!"
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    test_file = TestDocument(src=src)
    uploaded_file_id = "aaaa1111-bbbb-2222-cccc-3333dddd4444"
    signed_url = "https://custom.storage.com/signed"

    # Create custom client
    custom_client = Mock()
    custom_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)
    custom_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)

    # WHEN getting the signed URL using the mixin with a custom client
    result = test_file.get_signed_url(vellum_client=custom_client)

    # THEN the custom client should be used
    assert result == signed_url
    custom_client.uploaded_files.create.assert_called_once()
    custom_client.uploaded_files.retrieve.assert_called_once_with(uploaded_file_id, expiry_seconds=604800)


def test_vellum_file_mixin_get_signed_url_method_already_uploaded():
    """Test that VellumFileMixin.get_signed_url() works for already uploaded files."""

    # GIVEN a test document that's already uploaded using the mixin
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"
    test_file = TestDocument(src=src)
    signed_url = "https://storage.vellum.ai/files/signed"

    # WHEN getting the signed URL using the mixin's .get_signed_url() method
    with patch("vellum.utils.vellum_client.create_vellum_client") as mock_create_client:
        mock_client = Mock()
        mock_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)
        mock_create_client.return_value = mock_client

        result = test_file.get_signed_url()

        # THEN the signed URL should be returned without uploading again
        assert result == signed_url
        mock_client.uploaded_files.create.assert_not_called()
        mock_client.uploaded_files.retrieve.assert_called_once_with(file_id, expiry_seconds=604800)


def test_vellum_file_mixin_serialization_valid_base64():
    """Tests that serialization succeeds with valid base64 data URLs."""

    # GIVEN a test document with valid base64 content
    content = b"Hello, this is a test document!"
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:application/pdf;base64,{base64_content}"
    test_file = TestDocument(src=src)

    # WHEN serializing the document
    serialized = test_file.model_dump()

    # THEN the serialization should succeed and preserve the src
    assert serialized["src"] == src


def test_vellum_file_mixin_serialization_invalid_base64():
    """Tests that serialization raises an error for invalid base64 data URLs."""

    # GIVEN a test document with invalid base64 content
    invalid_base64 = "not-valid-base64!!!"
    src = f"data:application/pdf;base64,{invalid_base64}"
    test_file = TestDocument(src=src)

    # WHEN serializing the document
    # THEN a PydanticSerializationError should be raised with InvalidFileSourceError as the cause
    with pytest.raises(PydanticSerializationError, match="Invalid base64 encoding in PDF data URL"):
        test_file.model_dump()


def test_vellum_file_mixin_serialization_non_data_url():
    """Tests that serialization succeeds for non-data URL sources."""

    # GIVEN a test document with a regular URL source
    src = "https://example.com/document.pdf"
    test_file = TestDocument(src=src)

    # WHEN serializing the document
    serialized = test_file.model_dump()

    # THEN the serialization should succeed and preserve the src
    assert serialized["src"] == src


def test_vellum_file_mixin_serialization_vellum_uploaded_file():
    """Tests that serialization succeeds for vellum:uploaded-file sources."""

    # GIVEN a test document with a vellum:uploaded-file source
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"
    test_file = TestDocument(src=src)

    # WHEN serializing the document
    serialized = test_file.model_dump()

    # THEN the serialization should succeed and preserve the src
    assert serialized["src"] == src
