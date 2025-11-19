"""Tests for file extension inference utilities."""

import pytest

from vellum.utils.files.extensions import ensure_filename_with_extension


@pytest.mark.parametrize(
    ["filename", "mime_type", "expected"],
    [
        # None filename cases - should default to 'file' with inferred extension
        pytest.param(None, "application/pdf", "file.pdf", id="none_filename_pdf"),
        pytest.param(None, "image/png", "file.png", id="none_filename_png"),
        pytest.param(None, "image/jpeg", "file.jpg", id="none_filename_jpeg_normalized"),
        pytest.param(None, "text/plain", "file.txt", id="none_filename_txt"),
        pytest.param(None, "video/mp4", "file.mp4", id="none_filename_mp4"),
        pytest.param(None, "audio/mpeg", "file.mp3", id="none_filename_mp3"),
        pytest.param(None, "text/markdown", "file.md", id="none_filename_markdown"),
        pytest.param(None, "application/x-yaml", "file.yaml", id="none_filename_yaml_x"),
        pytest.param(None, "text/yaml", "file.yaml", id="none_filename_yaml_text"),
        pytest.param(None, "application/gzip", "file.gz", id="none_filename_gzip"),
        pytest.param(None, "application/xml", "file.xml", id="none_filename_xml_normalized"),
        pytest.param(None, "application/octet-stream", "file.bin", id="none_filename_octet_stream"),
        pytest.param(None, "application/x-unknown-type", "file.bin", id="none_filename_unknown_mime"),
        # Filename without extension - should add appropriate extension
        pytest.param("document", "application/pdf", "document.pdf", id="document_without_ext_pdf"),
        pytest.param("report", "application/pdf", "report.pdf", id="report_without_ext_pdf"),
        pytest.param(
            "report",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "report.docx",
            id="report_without_ext_docx",
        ),
        pytest.param("config", "application/x-yaml", "config.yaml", id="config_without_ext_yaml_x"),
        pytest.param("config", "text/yaml", "config.yaml", id="config_without_ext_yaml_text"),
        pytest.param("README", "text/markdown", "README.md", id="readme_without_ext_markdown"),
        pytest.param("data", "text/csv", "data.csv", id="data_without_ext_csv"),
        pytest.param("data", "application/octet-stream", "data.bin", id="data_without_ext_bin"),
        pytest.param("archive", "application/gzip", "archive.gz", id="archive_without_ext_gzip"),
        pytest.param("file", "application/pdf", "file.pdf", id="file_without_ext_pdf"),
        # Filename with extension - should keep existing extension
        pytest.param("document.pdf", "application/pdf", "document.pdf", id="document_pdf_with_ext"),
        pytest.param("image.png", "image/jpeg", "image.png", id="image_png_mismatched_mime"),
        pytest.param("data.csv", "text/csv", "data.csv", id="data_csv_with_ext"),
        pytest.param("config.yaml", "application/x-yaml", "config.yaml", id="config_yaml_with_ext"),
        # MIME type with parameters - should strip parameters
        pytest.param(None, "text/html; charset=utf-8", "file.html", id="none_filename_html_with_charset"),
        pytest.param("page", "text/html; charset=utf-8", "page.html", id="page_without_ext_html_with_charset"),
    ],
)
def test_ensure_filename_with_extension(filename, mime_type, expected):
    """Test filename extension inference for various filename and MIME type combinations."""
    result = ensure_filename_with_extension(filename, mime_type)
    assert result == expected
