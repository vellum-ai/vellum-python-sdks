from abc import ABC, abstractmethod
import importlib.abc
from io import StringIO
from typing import Optional


class BaseWorkflowFinder(importlib.abc.MetaPathFinder, ABC):
    """
    Abstract base class for workflow finders that support custom error message formatting.
    """

    @abstractmethod
    def format_error_message(self, error_message: str) -> str:
        """
        Format an error message to be more user-friendly.

        Args:
            error_message: The original error message

        Returns:
            The formatted error message
        """
        pass

    @abstractmethod
    def virtual_open(self, file_path: str) -> Optional[StringIO]:
        """
        Open a virtual file if it exists in this finder's namespace.

        Args:
            file_path: The absolute file path to open

        Returns:
            A StringIO object containing the file contents, or None if the file is not found
        """
        pass
