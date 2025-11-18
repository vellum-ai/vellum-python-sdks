import pytest
import base64
from unittest.mock import Mock, patch

from vellum import VellumAudio, VellumDocument, VellumImage, VellumVideo
from vellum.utils.files import InvalidFileSourceError, stream_vellum_file

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
def test_stream_vellum_file_base64_data_url(file_type, content, mime_type):
    """Test streaming files from base64 data URLs."""
    # Encode content as base64
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:{mime_type};base64,{base64_content}"

    # Create the appropriate file type
    vellum_file = file_type(src=src)

    # Stream the file and collect chunks
    chunks = []
    with stream_vellum_file(vellum_file) as chunk_iter:
        for chunk in chunk_iter:
            chunks.append(chunk)

    # Verify the content matches
    result = b"".join(chunks)
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
def test_stream_vellum_file_with_custom_chunk_size(file_type, content):
    """Test that custom chunk size is respected."""
    # Encode content as base64
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:application/octet-stream;base64,{base64_content}"

    vellum_file = file_type(src=src)

    # Stream with small chunk size
    chunk_size = 5
    chunks = []
    with stream_vellum_file(vellum_file, chunk_size=chunk_size) as chunk_iter:
        for chunk in chunk_iter:
            chunks.append(chunk)
            # Each chunk should be <= chunk_size (last chunk may be smaller)
            assert len(chunk) <= chunk_size

    # Verify the content matches when reassembled
    result = b"".join(chunks)
    assert result == content

    # Verify we got multiple chunks for content larger than chunk_size
    if len(content) > chunk_size:
        assert len(chunks) > 1


@pytest.mark.parametrize(
    "file_type",
    [VellumDocument, VellumImage, VellumAudio, VellumVideo],
)
def test_stream_vellum_file_from_url(file_type):
    """Test streaming files from direct URLs."""
    content = b"URL fetched content that will be streamed"
    url = "https://example.com/file.dat"

    vellum_file = file_type(src=url)

    with patch("vellum.utils.files.stream.requests.get") as mock_get:
        mock_response = Mock()
        # Simulate streaming response with iter_content
        mock_response.iter_content = Mock(return_value=iter([content[:20], content[20:]]))
        mock_response.raise_for_status = Mock()
        mock_response.close = Mock()
        mock_get.return_value = mock_response

        chunks = []
        with stream_vellum_file(vellum_file) as chunk_iter:
            for chunk in chunk_iter:
                chunks.append(chunk)

        result = b"".join(chunks)
        assert result == content
        mock_get.assert_called_once_with(url, stream=True)
        mock_response.raise_for_status.assert_called_once()
        mock_response.close.assert_called_once()


@pytest.mark.parametrize(
    "file_type",
    [VellumDocument, VellumImage, VellumAudio, VellumVideo],
)
def test_stream_vellum_file_from_vellum_uploaded_file(file_type):
    """Test streaming files from Vellum uploaded file IDs."""
    content = b"Vellum uploaded content to stream"
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

        # Mock the file download with streaming
        file_response = Mock()
        file_response.iter_content = Mock(return_value=iter([content[:15], content[15:]]))
        file_response.raise_for_status = Mock()
        file_response.close = Mock()

        mock_get.return_value = file_response

        chunks = []
        with stream_vellum_file(vellum_file) as chunk_iter:
            for chunk in chunk_iter:
                chunks.append(chunk)

        result = b"".join(chunks)
        assert result == content
        mock_client.uploaded_files.retrieve.assert_called_once_with(file_id)
        mock_get.assert_called_once_with(file_url, stream=True)
        file_response.close.assert_called_once()


def test_stream_vellum_file_context_manager_cleanup():
    """Test that the context manager properly cleans up resources."""
    content = b"Test content"
    base64_content = base64.b64encode(content).decode("utf-8")
    src = f"data:text/plain;base64,{base64_content}"

    vellum_file = VellumDocument(src=src)

    # Test that we can use the iterator only within the context
    with stream_vellum_file(vellum_file) as chunk_iter:
        chunks = list(chunk_iter)

    # After the context, the iterator should be exhausted
    assert b"".join(chunks) == content


def test_stream_vellum_file_invalid_src():
    """Test that invalid src raises InvalidFileSourceError even in streaming mode."""
    vellum_file = VellumDocument(src="invalid://source")

    with pytest.raises(InvalidFileSourceError, match="Invalid file source"):
        with stream_vellum_file(vellum_file) as chunk_iter:
            list(chunk_iter)


def test_stream_vellum_file_large_file_simulation():
    """Test streaming a large file to verify memory efficiency."""
    # Simulate a large file by creating content in chunks
    large_content = b"x" * 10000  # 10KB
    base64_content = base64.b64encode(large_content).decode("utf-8")
    src = f"data:application/octet-stream;base64,{base64_content}"

    vellum_file = VellumDocument(src=src)

    # Stream with 1KB chunks
    chunk_size = 1024
    total_bytes = 0
    chunk_count = 0

    with stream_vellum_file(vellum_file, chunk_size=chunk_size) as chunk_iter:
        for chunk in chunk_iter:
            total_bytes += len(chunk)
            chunk_count += 1
            assert len(chunk) <= chunk_size

    assert total_bytes == len(large_content)
    assert chunk_count >= len(large_content) // chunk_size
