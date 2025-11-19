import pytest
import base64
from unittest.mock import Mock, patch

import requests

from vellum import VellumAudio, VellumDocument, VellumImage, VellumVideo
from vellum.client.core.api_error import ApiError
from vellum.utils.files import FileNotFoundError, FileRetrievalError, InvalidFileSourceError, upload_vellum_file

# Sample content for different file types
SAMPLE_TEXT_CONTENT = b"This is a sample text document content."
SAMPLE_IMAGE_CONTENT = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"  # Minimal PNG header
SAMPLE_AUDIO_CONTENT = b"RIFF\x00\x00\x00\x00WAVEfmt "  # Minimal WAV header
SAMPLE_VIDEO_CONTENT = b"\x00\x00\x00\x20ftypmp42"  # Minimal MP4 header


@pytest.fixture
def mock_vellum_client():
    """Fixture that provides a mock Vellum client."""
    mock_client = Mock()
    with patch("vellum.utils.vellum_client.create_vellum_client", return_value=mock_client):
        yield mock_client


@pytest.mark.parametrize(
    ["file_type", "content", "mime_type"],
    [
        (VellumDocument, SAMPLE_TEXT_CONTENT, "text/plain"),
        (VellumImage, SAMPLE_IMAGE_CONTENT, "image/png"),
        (VellumAudio, SAMPLE_AUDIO_CONTENT, "audio/wav"),
        (VellumVideo, SAMPLE_VIDEO_CONTENT, "video/mp4"),
    ],
)
def test_upload_vellum_file_base64_data_url(mock_vellum_client, file_type, content, mime_type):
    """Test uploading files from base64 data URLs."""

    # GIVEN a VellumFile with a base64 data URL source
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:{mime_type};base64,{base64_content}"
    vellum_file = file_type(src=src)
    uploaded_file_id = "12345678-1234-1234-1234-123456789abc"
    mock_vellum_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)

    # WHEN uploading the file
    result = upload_vellum_file(vellum_file)

    # THEN the file should be uploaded with the correct mime type
    assert result.src == f"vellum:uploaded-file:{uploaded_file_id}"
    assert isinstance(result, file_type)
    mock_vellum_client.uploaded_files.create.assert_called_once()
    call_args = mock_vellum_client.uploaded_files.create.call_args
    uploaded_file_tuple = call_args.kwargs["file"]
    assert uploaded_file_tuple[2] == mime_type


@pytest.mark.parametrize(
    ["file_type", "content"],
    [
        (VellumDocument, SAMPLE_TEXT_CONTENT),
        (VellumImage, SAMPLE_IMAGE_CONTENT),
        (VellumAudio, SAMPLE_AUDIO_CONTENT),
        (VellumVideo, SAMPLE_VIDEO_CONTENT),
    ],
)
@patch("vellum.utils.files.upload.requests.get")
def test_upload_vellum_file_from_url(mock_get, mock_vellum_client, file_type, content):
    """Test uploading files from direct URLs."""

    # GIVEN a VellumFile with an HTTP/HTTPS URL source
    url = "https://example.com/file.dat"
    vellum_file = file_type(src=url)
    uploaded_file_id = "87654321-4321-4321-4321-210987654321"
    mock_response = Mock(content=content, headers={"content-type": "application/octet-stream"})
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    mock_vellum_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)

    # WHEN uploading the file
    result = upload_vellum_file(vellum_file)

    # THEN the file should be downloaded from the URL and uploaded to Vellum
    assert result.src == f"vellum:uploaded-file:{uploaded_file_id}"
    assert isinstance(result, file_type)
    mock_get.assert_called_once_with(url, stream=True)
    mock_response.raise_for_status.assert_called_once()
    mock_vellum_client.uploaded_files.create.assert_called_once()


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
def test_upload_vellum_file_already_uploaded(file_type):
    """Test that already uploaded files are returned unchanged."""

    # GIVEN a VellumFile that is already uploaded (has vellum:uploaded-file: src)
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"
    vellum_file = file_type(src=src)

    # WHEN uploading the file
    result = upload_vellum_file(vellum_file)

    # THEN the file should be returned unchanged without calling the API
    assert result is vellum_file
    assert result.src == src


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
def test_upload_vellum_file_with_custom_filename(mock_vellum_client, file_type):
    """Test uploading files with a custom filename."""

    # GIVEN a VellumFile and a custom filename
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    custom_filename = "my_custom_file.txt"
    vellum_file = file_type(src=src)
    uploaded_file_id = "aaaabbbb-cccc-dddd-eeee-ffff00001111"
    mock_vellum_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)

    # WHEN uploading the file with a custom filename
    result = upload_vellum_file(vellum_file, filename=custom_filename)

    # THEN the file should be uploaded with the custom filename
    assert result.src == f"vellum:uploaded-file:{uploaded_file_id}"
    assert isinstance(result, file_type)
    call_args = mock_vellum_client.uploaded_files.create.call_args
    uploaded_file_tuple = call_args.kwargs["file"]
    assert uploaded_file_tuple[0] == custom_filename


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
def test_upload_vellum_file_with_custom_client(file_type):
    """Test uploading files with a custom Vellum client."""

    # GIVEN a VellumFile and a custom Vellum client
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    vellum_file = file_type(src=src)
    uploaded_file_id = "custom-client-file-id"
    custom_client = Mock()
    custom_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)

    # WHEN uploading the file with the custom client
    result = upload_vellum_file(vellum_file, vellum_client=custom_client)

    # THEN the custom client should be used for the upload
    assert result.src == f"vellum:uploaded-file:{uploaded_file_id}"
    custom_client.uploaded_files.create.assert_called_once()


@pytest.mark.parametrize("file_type", [VellumDocument, VellumImage, VellumAudio, VellumVideo])
def test_upload_vellum_file_preserves_metadata(mock_vellum_client, file_type):
    """Test that file metadata is preserved during upload."""

    # GIVEN a VellumFile with metadata
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    metadata = {"key1": "value1", "key2": 42, "key3": {"nested": "value"}}
    vellum_file = file_type(src=src, metadata=metadata)
    uploaded_file_id = "metadata-test-file-id"
    mock_vellum_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)

    # WHEN uploading the file
    result = upload_vellum_file(vellum_file)

    # THEN the metadata should be preserved in the returned file
    assert result.src == f"vellum:uploaded-file:{uploaded_file_id}"
    assert result.metadata == metadata


def test_upload_vellum_file_invalid_src():
    """Test that invalid src raises InvalidFileSourceError."""

    # GIVEN a VellumFile with an invalid source format
    vellum_file = VellumDocument(src="invalid://source")

    # WHEN uploading the file
    # THEN an InvalidFileSourceError should be raised
    with pytest.raises(InvalidFileSourceError, match="Invalid file source"):
        upload_vellum_file(vellum_file)


@patch("vellum.utils.files.upload.requests.get")
def test_upload_vellum_file_url_not_found(mock_get):
    """Test handling of 404 errors when downloading from URL."""

    # GIVEN a VellumFile with a URL that returns a 404 error
    url = "https://example.com/nonexistent.dat"
    vellum_file = VellumDocument(src=url)
    mock_response = Mock(status_code=404)
    http_error = requests.HTTPError()
    http_error.response = mock_response
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    # WHEN uploading the file
    # THEN a FileNotFoundError should be raised
    with pytest.raises(FileNotFoundError, match="File not found at URL"):
        upload_vellum_file(vellum_file)


@patch("vellum.utils.files.upload.requests.get")
def test_upload_vellum_file_url_network_error(mock_get):
    """Test handling of network errors when downloading from URL."""

    # GIVEN a VellumFile with a URL that causes a network error
    url = "https://example.com/file.dat"
    vellum_file = VellumDocument(src=url)
    mock_get.side_effect = requests.RequestException("Network error")

    # WHEN uploading the file
    # THEN a FileRetrievalError should be raised
    with pytest.raises(FileRetrievalError, match="Network error while retrieving file"):
        upload_vellum_file(vellum_file)


@patch("vellum.utils.files.upload.requests.get")
def test_upload_vellum_file_url_http_error(mock_get):
    """Test handling of HTTP errors (non-404) when downloading from URL."""

    # GIVEN a VellumFile with a URL that returns a 403 error
    url = "https://example.com/forbidden.dat"
    vellum_file = VellumDocument(src=url)
    mock_response = Mock(status_code=403)
    http_error = requests.HTTPError()
    http_error.response = mock_response
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    # WHEN uploading the file
    # THEN a FileRetrievalError should be raised
    with pytest.raises(FileRetrievalError, match="Failed to retrieve file from URL"):
        upload_vellum_file(vellum_file)


def test_upload_vellum_file_api_error_on_create(mock_vellum_client):
    """Test handling of API errors during file upload."""

    # GIVEN a VellumFile and a Vellum client that raises an API error
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    vellum_file = VellumDocument(src=src)
    mock_vellum_client.uploaded_files.create.side_effect = ApiError(status_code=500, body="Internal server error")

    # WHEN uploading the file
    # THEN a FileRetrievalError should be raised
    with pytest.raises(FileRetrievalError, match="Failed to upload file to Vellum"):
        upload_vellum_file(vellum_file)


@pytest.mark.parametrize(
    ["src_pattern", "file_type"],
    [
        ("vellum:uploaded-file:12345678-1234-1234-1234-123456789abc", VellumDocument),
        ("VELLUM:UPLOADED-FILE:12345678-1234-1234-1234-123456789abc", VellumImage),
        ("Vellum:Uploaded-File:12345678-1234-1234-1234-123456789abc", VellumAudio),
    ],
)
def test_upload_vellum_file_case_insensitive_vellum_src(src_pattern, file_type):
    """Test that vellum:uploaded-file: pattern matching is case insensitive."""

    # GIVEN a VellumFile with a vellum:uploaded-file: src in various cases
    vellum_file = file_type(src=src_pattern)

    # WHEN uploading the file
    result = upload_vellum_file(vellum_file)

    # THEN the file should be returned unchanged regardless of case
    assert result is vellum_file
    assert result.src == src_pattern


def test_upload_vellum_file_none_filename(mock_vellum_client):
    """Test uploading file with filename=None defaults to 'file' with inferred extension."""

    # GIVEN a VellumFile and filename=None
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"
    vellum_file = VellumDocument(src=src)
    uploaded_file_id = "none-filename-test"
    mock_vellum_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)

    # WHEN uploading the file with filename=None
    result = upload_vellum_file(vellum_file, filename=None)

    # THEN the file should be uploaded with 'file.txt' as the filename (inferred from MIME type)
    assert result.src == f"vellum:uploaded-file:{uploaded_file_id}"
    call_args = mock_vellum_client.uploaded_files.create.call_args
    uploaded_file_tuple = call_args.kwargs["file"]
    assert uploaded_file_tuple[0] == "file.txt"


def test_upload_vellum_file_filename_without_extension(mock_vellum_client):
    """Test uploading file with filename without extension auto-adds extension."""

    # GIVEN a VellumFile and a filename without extension
    base64_content = base64.b64encode(SAMPLE_TEXT_CONTENT).decode("utf-8")
    src = f"data:application/pdf;base64,{base64_content}"
    vellum_file = VellumDocument(src=src)
    uploaded_file_id = "no-ext-filename-test"
    mock_vellum_client.uploaded_files.create.return_value = Mock(id=uploaded_file_id)

    # WHEN uploading the file with a filename without extension
    result = upload_vellum_file(vellum_file, filename="report")

    # THEN the file should be uploaded with extension added based on MIME type
    assert result.src == f"vellum:uploaded-file:{uploaded_file_id}"
    call_args = mock_vellum_client.uploaded_files.create.call_args
    uploaded_file_tuple = call_args.kwargs["file"]
    assert uploaded_file_tuple[0] == "report.pdf"
