import base64
from unittest.mock import Mock, patch

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
