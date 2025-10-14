from abc import ABC, abstractmethod
import importlib.abc


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
