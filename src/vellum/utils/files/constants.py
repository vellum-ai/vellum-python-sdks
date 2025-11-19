"""Constants for Vellum file handling."""

# Regex pattern to match Vellum uploaded file IDs in the format:
# vellum:uploaded-file:12345678-1234-1234-1234-123456789abc
VELLUM_FILE_SRC_PATTERN = r"vellum:uploaded-file:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$"

# Regex pattern to match base64 data URLs with optional MIME type and charset:
# data:text/plain;charset=utf-8;base64,SGVsbG8=
# data:image/png;base64,iVBORw0KGgo=
# data:;base64,
BASE64_DATA_URL_PATTERN = (
    r"^data:([a-zA-Z0-9+/.-]+/[a-zA-Z0-9+.-]+)?(;charset=[a-zA-Z0-9-]+)?;base64,(.*)$"  # noqa: E501
)

# Regex pattern to match HTTP/HTTPS URLs
URL_PATTERN = r"^(https?://[^\s]+)$"

# Fallback MIME type to file extension mappings for types that mimetypes.guess_extension
# might not handle well or returns undesirable extensions
MIME_TYPE_TO_EXTENSION = {
    "application/octet-stream": ".bin",
    "text/plain": ".txt",
    # Markdown variants
    "text/markdown": ".md",
    "text/x-markdown": ".md",
    # YAML variants
    "application/x-yaml": ".yaml",
    "text/yaml": ".yaml",
    "application/yaml": ".yaml",
    # Compression formats
    "application/gzip": ".gz",
    "application/x-gzip": ".gz",
}

# File extension overrides to prefer more common extensions
EXTENSION_OVERRIDES = {
    # Image formats - prefer shorter extensions
    ".jpe": ".jpg",
    ".jpeg": ".jpg",
    ".tif": ".tiff",
    # HTML - prefer .html over .htm
    ".htm": ".html",
    # XML - prefer .xml over .xsl (mimetypes returns .xsl for application/xml)
    ".xsl": ".xml",
    # YAML - prefer .yaml over .yml for consistency
    ".yml": ".yaml",
}
