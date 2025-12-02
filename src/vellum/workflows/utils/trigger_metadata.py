"""Utility functions for reading trigger attribute metadata from metadata.json."""

from functools import lru_cache
import json
import os
from uuid import UUID
from typing import TYPE_CHECKING, Dict, Optional, Type

from vellum.workflows.utils.files import virtual_open

if TYPE_CHECKING:
    from vellum.workflows.triggers.base import BaseTrigger


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
    # Local import to avoid circular dependency: triggers.base imports references.trigger,
    # which in turn imports this module.
    from vellum.workflows.triggers import base as triggers_base

    try:
        # Find the workflow root that contains metadata.json
        workflow_root = triggers_base._find_workflow_root_with_metadata(module_path)
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
    # Local import to avoid circular dependency: triggers.base imports references.trigger,
    # which in turn imports this module.
    from vellum.workflows.triggers import base as triggers_base

    workflow_root = triggers_base._find_workflow_root_with_metadata(trigger_class.__module__)
    if not workflow_root:
        return None

    attribute_mapping = _get_trigger_attribute_id_mapping(trigger_class.__module__)
    if not attribute_mapping:
        return None

    # Convert module path to relative path and append class name
    # e.g., "root_module.triggers.scheduled" + "ScheduleTrigger" -> ".triggers.scheduled.ScheduleTrigger"
    relative_module_path = triggers_base._convert_to_relative_module_path(trigger_class.__module__, workflow_root)
    if not relative_module_path:
        return None

    # Build the key: "<trigger_path>|<attribute_key>"
    relative_trigger_path = f"{relative_module_path}.{trigger_class.__qualname__}"
    key = f"{relative_trigger_path}|{attribute_name}"
    return attribute_mapping.get(key)
