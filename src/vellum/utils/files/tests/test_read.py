import pytest
import base64
from unittest.mock import Mock, patch

from vellum import VellumAudio, VellumDocument, VellumImage, VellumVideo
from vellum.utils.files import FileRetrievalError, InvalidFileSourceError, read_vellum_file

# Sample content for different file types
SAMPLE_TEXT_CONTENT = b"This is a sample text document content."
SAMPLE_IMAGE_CONTENT = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"  # Minimal PNG header
SAMPLE_AUDIO_CONTENT = b"RIFF\x00\x00\x00\x00WAVEfmt "  # Minimal WAV header
SAMPLE_VIDEO_CONTENT = b"\x00\x00\x00\x20ftypmp42"  # Minimal MP4 header


@pytest.mark.parametrize(
    ["file_type", "content", "mime_type"],
    [
        (VellumDocument, SAMPLE_TEXT_CONTENT, "text/plain"),
        (VellumImage, SAMPLE_IMAGE_CONTENT, "image/png"),
        (VellumAudio, SAMPLE_AUDIO_CONTENT, "audio/wav"),
        (VellumVideo, SAMPLE_VIDEO_CONTENT, "video/mp4"),
    ],
)
def test_read_vellum_file_base64_data_url_with_mime_type(file_type, content, mime_type):
    """Test reading files from base64 data URLs with MIME types."""
    # Encode content as base64
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:{mime_type};base64,{base64_content}"

    # Create the appropriate file type
    vellum_file = file_type(src=src)

    # Read the file
    result = read_vellum_file(vellum_file)

    # Verify the content matches
    assert result == content


@pytest.mark.parametrize(
    ["file_type", "content"],
    [
        (VellumDocument, SAMPLE_TEXT_CONTENT),
        (VellumImage, SAMPLE_IMAGE_CONTENT),
        (VellumAudio, SAMPLE_AUDIO_CONTENT),
        (VellumVideo, SAMPLE_VIDEO_CONTENT),
    ],
)
def test_read_vellum_file_base64_data_url_without_mime_type(file_type, content):
    """Test reading files from base64 data URLs without MIME types."""
    # Encode content as base64
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:;base64,{base64_content}"

    # Create the appropriate file type
    vellum_file = file_type(src=src)

    # Read the file
    result = read_vellum_file(vellum_file)

    # Verify the content matches
    assert result == content


@pytest.mark.parametrize(
    ["file_type", "content", "mime_type", "charset"],
    [
        (VellumDocument, SAMPLE_TEXT_CONTENT, "text/plain", "utf-8"),
        (VellumDocument, SAMPLE_TEXT_CONTENT, "text/html", "iso-8859-1"),
        (VellumImage, SAMPLE_IMAGE_CONTENT, "image/png", "utf-8"),
    ],
)
def test_read_vellum_file_base64_data_url_with_charset(file_type, content, mime_type, charset):
    """Test reading files from base64 data URLs with charset specifications."""
    # Encode content as base64
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:{mime_type};charset={charset};base64,{base64_content}"

    # Create the appropriate file type
    vellum_file = file_type(src=src)

    # Read the file
    result = read_vellum_file(vellum_file)

    # Verify the content matches
    assert result == content


@pytest.mark.parametrize(
    ["file_type", "content"],
    [
        (VellumDocument, b""),  # Empty file
        (VellumImage, b"x" * 1000),  # Larger content
        (VellumAudio, b"\x00\x01\x02\x03\x04"),  # Binary content with special bytes
        (VellumVideo, b"Unicode content: \xc3\xa9\xc3\xa0\xc3\xb1"),  # UTF-8 encoded content
    ],
)
def test_read_vellum_file_base64_edge_cases(file_type, content):
    """Test reading files with edge case content (empty, large, special characters)."""
    # Encode content as base64
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:application/octet-stream;base64,{base64_content}"

    # Create the appropriate file type
    vellum_file = file_type(src=src)

    # Read the file
    result = read_vellum_file(vellum_file)

    # Verify the content matches
    assert result == content


@pytest.mark.parametrize(
    "file_type",
    [VellumDocument, VellumImage, VellumAudio, VellumVideo],
)
def test_read_vellum_file_from_url(file_type):
    """Test reading files from direct URLs."""
    content = b"URL fetched content"
    url = "https://example.com/file.dat"

    vellum_file = file_type(src=url)

    with patch("vellum.utils.files.stream.requests.get") as mock_get:
        mock_response = Mock()
        # Mock streaming interface
        mock_response.iter_content = Mock(return_value=iter([content]))
        mock_response.raise_for_status = Mock()
        mock_response.close = Mock()
        mock_get.return_value = mock_response

        result = read_vellum_file(vellum_file)

        assert result == content
        mock_get.assert_called_once_with(url, stream=True)
        mock_response.raise_for_status.assert_called_once()
        mock_response.close.assert_called_once()


@pytest.mark.parametrize(
    "file_type",
    [VellumDocument, VellumImage, VellumAudio, VellumVideo],
)
def test_read_vellum_file_from_vellum_uploaded_file(file_type):
    """Test reading files from Vellum uploaded file IDs."""
    content = b"Vellum uploaded content"
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"
    file_url = "https://s3.amazonaws.com/example/file.dat"

    vellum_file = file_type(src=src)

    with patch("vellum.utils.vellum_client.create_vellum_client") as mock_create_client, patch(
        "vellum.utils.files.stream.requests.get"
    ) as mock_get:
        # Mock the Vellum client
        mock_client = Mock()
        uploaded_file_mock = Mock()
        uploaded_file_mock.file_url = file_url
        mock_client.uploaded_files.retrieve.return_value = uploaded_file_mock
        mock_create_client.return_value = mock_client

        # Mock the file download with streaming interface
        file_response = Mock()
        file_response.iter_content = Mock(return_value=iter([content]))
        file_response.raise_for_status = Mock()
        file_response.close = Mock()

        mock_get.return_value = file_response

        result = read_vellum_file(vellum_file)

        assert result == content
        mock_client.uploaded_files.retrieve.assert_called_once_with(file_id)
        mock_get.assert_called_once_with(file_url, stream=True)
        file_response.close.assert_called_once()


def test_read_vellum_file_invalid_src():
    """Test that invalid src raises InvalidFileSourceError."""
    vellum_file = VellumDocument(src="invalid://source")

    with pytest.raises(InvalidFileSourceError, match="Invalid file source"):
        read_vellum_file(vellum_file)


def test_read_vellum_file_vellum_uploaded_file_missing_url():
    """Test that missing file_url in API response raises FileRetrievalError."""
    file_id = "12345678-1234-1234-1234-123456789abc"
    src = f"vellum:uploaded-file:{file_id}"

    vellum_file = VellumDocument(src=src)

    # Mock the create_vellum_client to return a client with an uploaded file without a file_url
    with patch("vellum.utils.vellum_client.create_vellum_client") as mock_create_client:
        mock_client = Mock()
        uploaded_file_mock = Mock()
        uploaded_file_mock.file_url = None
        mock_client.uploaded_files.retrieve.return_value = uploaded_file_mock
        mock_create_client.return_value = mock_client

        with pytest.raises(FileRetrievalError, match="has no accessible URL"):
            read_vellum_file(vellum_file)
