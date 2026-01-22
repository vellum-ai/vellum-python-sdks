import sys

from vellum.workflows.loaders.base import BaseWorkflowFinder


def normalize_module_path(module_path: str) -> str:
    """
    Normalize a module path by filtering out a leading ephemeral namespace segment.

    When workflows are loaded dynamically (e.g., via VirtualFileFinder), the module path
    may start with an ephemeral namespace that changes on each invocation. This function
    strips that leading segment to ensure stable, deterministic ID generation.

    The function checks if the first segment of the module path exactly matches the
    namespace of any registered BaseWorkflowFinder in sys.meta_path. Only namespaces
    that are actually registered are stripped, preventing accidental stripping of
    legitimate module names.

    Args:
        module_path: The module path to normalize (e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890.workflow"
                     or "workflow_tmp_ABC123xyz.workflow")

    Returns:
        The normalized module path with the leading ephemeral segment removed if present
        (e.g., "workflow")
    """
    parts = module_path.split(".")
    if not parts:
        return module_path

    first_part = parts[0]

    # Check if the first part matches the namespace of any registered workflow finder
    for finder in sys.meta_path:
        if isinstance(finder, BaseWorkflowFinder) and finder.namespace == first_part:
            return ".".join(parts[1:]) if len(parts) > 1 else ""

    return module_path
