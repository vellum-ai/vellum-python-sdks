"""File utilities for workflows, including virtual file support."""

import sys

from vellum.workflows.loaders.base import BaseWorkflowFinder


def virtual_open(file_path: str):
    """
    Open a file, checking BaseWorkflowFinder instances first before falling back to regular open().

    This function is used to support reading files in both regular and virtual environments
    (e.g., when using VirtualFileLoader in serverless/Vembda deployments).

    Args:
        file_path: Path to the file to open

    Returns:
        A file-like object (either StringIO or a regular file handle)
    """
    # Check if there's a BaseWorkflowFinder in sys.meta_path
    for finder in sys.meta_path:
        if isinstance(finder, BaseWorkflowFinder):
            result = finder.virtual_open(file_path)
            if result is not None:
                return result

    return open(file_path)
