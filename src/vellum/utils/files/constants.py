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
