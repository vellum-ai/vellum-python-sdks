"""Utility functions for reading trigger metadata from metadata.json."""

from functools import lru_cache
import json
import os
from uuid import UUID
from typing import TYPE_CHECKING, Dict, Optional, Type

from vellum.workflows.utils.files import virtual_open

if TYPE_CHECKING:
    from vellum.workflows.triggers.base import BaseTrigger


def _convert_to_relative_module_path(absolute_module_path: str, workflow_root: str) -> str:
    """
    Convert an absolute module path to a relative path from the workflow root.

    Args:
        absolute_module_path: The full module path (e.g., "workflow_id.triggers.scheduled")
        workflow_root: The workflow root module (e.g., "workflow_id")

    Returns:
        Relative module path with leading dot (e.g., ".triggers.scheduled")
    """
    if not absolute_module_path.startswith(workflow_root):
        return ""

    remaining_path = absolute_module_path[len(workflow_root) :]
    if remaining_path.startswith("."):
        return remaining_path
    else:
        return "." + remaining_path


def _find_workflow_root_with_metadata(trigger_module: str) -> Optional[str]:
    """
    Find the workflow root module by searching for metadata.json up the module hierarchy.

    Args:
        trigger_module: The trigger's module path (e.g., "workflows.my_workflow.triggers.my_trigger")

    Returns:
        The workflow root module path if found, None otherwise
    """
    module_parts = trigger_module.split(".")

    # Try searching up the module hierarchy for metadata.json
    for i in range(len(module_parts), 0, -1):
        potential_root = ".".join(module_parts[:i])
        module_dir = potential_root.replace(".", os.path.sep)
        metadata_path = os.path.join(module_dir, "metadata.json")

        # Try to open the file using virtual_open to support both regular and virtual filesystems
        # virtual_open checks BaseWorkflowFinder instances before falling back to regular open()
        try:
            file_handle = virtual_open(metadata_path)
            if file_handle is not None:
                file_handle.close()
                return potential_root
        except (FileNotFoundError, OSError):
            pass

    return None


@lru_cache(maxsize=128)
def _get_trigger_attribute_id_mapping(module_path: str) -> Dict[str, UUID]:
    """
    Read trigger attribute ID mapping from metadata.json for a given module.

    This function is cached to avoid repeated file reads. It searches up the module
    hierarchy for metadata.json and extracts the trigger_attribute_id_mapping.

    Args:
        module_path: The module path to search from (e.g., "workflows.my_workflow.triggers.my_trigger")

    Returns:
        Dictionary mapping "<trigger_path>|<attribute_key>" to their UUIDs
    """
    try:
        # Find the workflow root that contains metadata.json
        workflow_root = _find_workflow_root_with_metadata(module_path)
        if not workflow_root:
            return {}

        # Convert module path to file path
        module_dir = workflow_root.replace(".", os.path.sep)
        metadata_path = os.path.join(module_dir, "metadata.json")

        # Use virtual_open to support both regular and virtual environments
        with virtual_open(metadata_path) as f:
            metadata_json = json.load(f)
            raw_mapping = metadata_json.get("trigger_attribute_id_mapping", {}) or {}

        # Convert string IDs to UUIDs, skipping invalid entries
        result: Dict[str, UUID] = {}
        for key, id_str in raw_mapping.items():
            try:
                result[key] = UUID(id_str)
            except ValueError:
                # Skip invalid UUID entries; they will fall back to hash-based IDs
                continue

        return result

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # If there's any error reading or parsing the file, return empty dict
        return {}


def get_trigger_attribute_id_from_metadata(trigger_class: "Type[BaseTrigger]", attribute_name: str) -> Optional[UUID]:
    """
    Get the trigger attribute ID from metadata.json for a given trigger class and attribute name.

    Args:
        trigger_class: The trigger class containing the attribute
        attribute_name: The name of the attribute

    Returns:
        The UUID from metadata.json, or None if not found
    """
    workflow_root = _find_workflow_root_with_metadata(trigger_class.__module__)
    if not workflow_root:
        return None

    attribute_mapping = _get_trigger_attribute_id_mapping(trigger_class.__module__)
    if not attribute_mapping:
        return None

    # Convert module path to relative path and append class name
    # e.g., "root_module.triggers.scheduled" + "ScheduleTrigger" -> ".triggers.scheduled.ScheduleTrigger"
    relative_module_path = _convert_to_relative_module_path(trigger_class.__module__, workflow_root)
    if not relative_module_path:
        return None

    # Build the key: "<trigger_path>|<attribute_key>"
    relative_trigger_path = f"{relative_module_path}.{trigger_class.__qualname__}"
    key = f"{relative_trigger_path}|{attribute_name}"
    return attribute_mapping.get(key)
