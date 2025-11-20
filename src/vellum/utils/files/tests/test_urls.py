import pytest
import base64
from unittest.mock import Mock, patch

from vellum import VellumAudio, VellumDocument, VellumImage, VellumVideo
from vellum.client.core.api_error import ApiError
from vellum.utils.files.exceptions import FileRetrievalError, InvalidFileSourceError
from vellum.utils.files.urls import get_signed_url

# Sample content for testing
SAMPLE_TEXT_CONTENT = b"This is a sample text document content."


@pytest.fixture
def mock_vellum_client():
    """Fixture that provides a mock Vellum client."""
    mock_client = Mock()
    with patch("vellum.utils.vellum_client.create_vellum_client", return_value=mock_client):
        yield mock_client


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
def test_get_signed_url_from_base64(mock_vellum_client, file_type):
    """Test getting signed URL for a file with base64 data URL source."""

    # GIVEN a VellumFile with a base64 data URL source
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    vellum_file = file_type(src=src)
    uploaded_file_id = "12345678-1234-1234-1234-123456789abc"
    signed_url = "https://example.com/signed-url?token=abc123"

    # Configure mock client
    mock_vellum_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)
    mock_vellum_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)

    # WHEN getting the signed URL
    result = get_signed_url(vellum_file)

    # THEN the file should be uploaded and signed URL returned
    assert result == signed_url
    mock_vellum_client.uploaded_files.create.assert_called_once()
    mock_vellum_client.uploaded_files.retrieve.assert_called_once_with(uploaded_file_id, expiry_seconds=604800)


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
@patch("vellum.utils.files.upload.requests.get")
def test_get_signed_url_from_http_url(mock_get, mock_vellum_client, file_type):
    """Test getting signed URL for a file with HTTP URL source."""

    # GIVEN a VellumFile with an HTTP URL source
    url = "https://example.com/file.dat"
    vellum_file = file_type(src=url)
    uploaded_file_id = "87654321-4321-4321-4321-210987654321"
    signed_url = "https://storage.vellum.ai/signed-url?token=xyz789"

    # Configure mock HTTP response
    mock_response = Mock(content=SAMPLE_TEXT_CONTENT, headers={"content-type": "application/octet-stream"})
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    # Configure mock client
    mock_vellum_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)
    mock_vellum_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)

    # WHEN getting the signed URL
    result = get_signed_url(vellum_file)

    # THEN the file should be downloaded, uploaded, and signed URL returned
    assert result == signed_url
    mock_get.assert_called_once_with(url, stream=True)
    mock_vellum_client.uploaded_files.create.assert_called_once()
    mock_vellum_client.uploaded_files.retrieve.assert_called_once_with(uploaded_file_id, expiry_seconds=604800)


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
def test_get_signed_url_already_uploaded(mock_vellum_client, file_type):
    """Test getting signed URL for a file that's already uploaded."""

    # GIVEN a VellumFile that is already uploaded (has vellum:uploaded-file: src)
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"
    vellum_file = file_type(src=src)
    signed_url = "https://storage.vellum.ai/files/signed?id=123"

    # Configure mock client
    mock_vellum_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)

    # WHEN getting the signed URL
    result = get_signed_url(vellum_file)

    # THEN the signed URL should be returned without uploading again
    assert result == signed_url
    mock_vellum_client.uploaded_files.create.assert_not_called()
    mock_vellum_client.uploaded_files.retrieve.assert_called_once_with(file_id, expiry_seconds=604800)


@pytest.mark.parametrize(
    ["src_pattern"],
    [
        ("vellum:uploaded-file:12345678-1234-1234-1234-123456789abc",),
        ("VELLUM:UPLOADED-FILE:12345678-1234-1234-1234-123456789abc",),
        ("Vellum:Uploaded-File:12345678-1234-1234-1234-123456789abc",),
    ],
)
def test_get_signed_url_case_insensitive_vellum_src(mock_vellum_client, src_pattern):
    """Test that vellum:uploaded-file: pattern matching is case insensitive."""

    # GIVEN a VellumFile with a vellum:uploaded-file: src in various cases
    file_id = "12345678-1234-1234-1234-123456789abc"
    vellum_file = VellumDocument(src=src_pattern)
    signed_url = "https://storage.vellum.ai/files/signed"

    # Configure mock client
    mock_vellum_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)

    # WHEN getting the signed URL
    result = get_signed_url(vellum_file)

    # THEN the signed URL should be returned regardless of case
    assert result == signed_url
    mock_vellum_client.uploaded_files.retrieve.assert_called_once_with(file_id, expiry_seconds=604800)


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
@patch("vellum.utils.files.urls.upload_vellum_file")
def test_get_signed_url_with_custom_client(mock_upload, file_type):
    """Test getting signed URL with a custom Vellum client."""

    # GIVEN a VellumFile and a custom Vellum client
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    vellum_file = file_type(src=src)
    uploaded_file_id = "aaaabbbb-cccc-dddd-eeee-111122223333"
    signed_url = "https://custom.storage.com/signed"

    # Create custom client
    custom_client = Mock()
    custom_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)

    # Mock upload_vellum_file to return an uploaded file
    mock_upload.return_value = file_type(src=f"vellum:uploaded-file:{uploaded_file_id}")

    # WHEN getting the signed URL with the custom client
    result = get_signed_url(vellum_file, vellum_client=custom_client)

    # THEN the custom client should be used
    assert result == signed_url
    mock_upload.assert_called_once_with(vellum_file, vellum_client=custom_client)
    custom_client.uploaded_files.retrieve.assert_called_once_with(uploaded_file_id, expiry_seconds=604800)


def test_get_signed_url_invalid_uploaded_file_format(mock_vellum_client):
    """Test that InvalidFileSourceError is raised when uploaded file ID cannot be parsed."""

    # GIVEN a VellumFile with a malformed vellum:uploaded-file: src
    # This should never happen in practice but we test error handling
    vellum_file = VellumDocument(src="vellum:uploaded-file:invalid-id-format")

    # Configure mock to return an uploaded file with malformed src
    mock_vellum_client.uploaded_files.create.return_value = Mock(id="invalid-id")

    # Mock the upload_vellum_file to return a file with invalid src
    with patch("vellum.utils.files.urls.upload_vellum_file") as mock_upload:
        mock_upload.return_value = VellumDocument(src="vellum:uploaded-file:not-a-valid-uuid")

        # WHEN getting the signed URL
        # THEN an InvalidFileSourceError should be raised
        with pytest.raises(InvalidFileSourceError, match="Failed to determine id of uploaded file"):
            get_signed_url(vellum_file)


def test_get_signed_url_api_error_on_retrieve(mock_vellum_client):
    """Test handling of API errors when retrieving signed URL."""

    # GIVEN a VellumFile that is already uploaded
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"
    vellum_file = VellumDocument(src=src)

    # Configure mock client to raise an API error on retrieve
    mock_vellum_client.uploaded_files.retrieve.side_effect = ApiError(status_code=404, body="File not found")

    # WHEN getting the signed URL
    # THEN a FileRetrievalError should be raised wrapping the API error
    with pytest.raises(FileRetrievalError, match="Failed to retrieve file from Vellum"):
        get_signed_url(vellum_file)


def test_get_signed_url_missing_signed_url(mock_vellum_client):
    """Test that FileRetrievalError is raised when signed URL is None."""

    # GIVEN a VellumFile that is already uploaded
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"
    vellum_file = VellumDocument(src=src)

    # Configure mock client to return None for file_url
    mock_vellum_client.uploaded_files.retrieve.return_value = Mock(file_url=None)

    # WHEN getting the signed URL
    # THEN a FileRetrievalError should be raised
    with pytest.raises(FileRetrievalError, match="Failed to retrieve signed URL"):
        get_signed_url(vellum_file)


def test_get_signed_url_uses_default_client_when_not_provided(mock_vellum_client):
    """Test that a default client is created when vellum_client is not provided."""

    # GIVEN a VellumFile and no custom client
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"
    vellum_file = VellumDocument(src=src)
    signed_url = "https://storage.vellum.ai/files/signed"

    # Configure mock client
    mock_vellum_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)

    # WHEN getting the signed URL without providing a client
    result = get_signed_url(vellum_file)

    # THEN the default client should be created and used
    assert result == signed_url
    mock_vellum_client.uploaded_files.retrieve.assert_called_once_with(file_id, expiry_seconds=604800)


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
@patch("vellum.utils.files.urls.upload_vellum_file")
def test_get_signed_url_preserves_file_type(mock_upload, mock_vellum_client, file_type):
    """Test that the file type is preserved through upload and retrieval."""

    # GIVEN a VellumFile of a specific type
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    vellum_file = file_type(src=src)
    uploaded_file_id = "11112222-3333-4444-5555-666677778888"
    signed_url = "https://storage.vellum.ai/files/typed"

    # Mock upload_vellum_file to return an uploaded file
    mock_upload.return_value = file_type(src=f"vellum:uploaded-file:{uploaded_file_id}")

    # Configure mock client
    mock_vellum_client.uploaded_files.retrieve.return_value = Mock(file_url=signed_url)

    # WHEN getting the signed URL
    result = get_signed_url(vellum_file)

    # THEN the signed URL should be returned
    assert result == signed_url
    # The file type should be consistent throughout the process
    mock_upload.assert_called_once_with(vellum_file, vellum_client=None)
    mock_vellum_client.uploaded_files.retrieve.assert_called_once_with(uploaded_file_id, expiry_seconds=604800)
