"""Exceptions for Vellum file operations."""


class VellumFileError(Exception):
    """Base exception for all Vellum file errors."""

    pass


class InvalidFileSourceError(VellumFileError):
    """Raised when a file source URL/identifier is malformed or unsupported."""

    pass


class FileRetrievalError(VellumFileError):
    """Raised when a file cannot be retrieved from its source."""

    pass


class FileNotFoundError(FileRetrievalError):
    """Raised when a file cannot be found at its source."""

    pass
