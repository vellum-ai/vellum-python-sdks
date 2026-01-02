"""Utilities for reading and managing workflow metadata.json files."""

import json
import os
from uuid import UUID
from typing import Any, Dict, Optional, Tuple, Type

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.utils.files import virtual_open


def find_workflow_root_with_metadata(module_path: str) -> Optional[str]:
    """
    Find the workflow root module by searching for metadata.json up the module hierarchy.

    Args:
        module_path: The module path to search from (e.g., "workflows.my_workflow.nodes.my_node")

    Returns:
        The workflow root module path if found, None otherwise
    """
    parts = module_path.split(".")
    for i in range(len(parts), 0, -1):
        potential_root = ".".join(parts[:i])
        file_path = os.path.join(potential_root.replace(".", os.path.sep), "metadata.json")
        try:
            f = virtual_open(file_path)
            if f is not None:
                f.close()
                return potential_root
        except (FileNotFoundError, OSError):
            continue
    return None


def _load_workflow_metadata(module_path: str) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Load the full metadata.json content for a given module.

    This function searches up the module hierarchy for metadata.json and loads its content.

    Args:
        module_path: The module path to search from (e.g., "workflows.my_workflow")

    Returns:
        A tuple of (workflow_root, metadata_dict). Returns (None, None) if not found.
    """
    try:
        workflow_root = find_workflow_root_with_metadata(module_path)
        if not workflow_root:
            return None, None
        file_path = os.path.join(workflow_root.replace(".", os.path.sep), "metadata.json")
        with virtual_open(file_path) as f:
            data = json.load(f)
            return workflow_root, data
    except Exception:
        return None, None


def _load_edges_mapping(module_path: str) -> Tuple[Optional[str], Dict[str, str]]:
    """
    Load edge path to ID mapping from metadata.json for a given module.

    This function searches up the module hierarchy for metadata.json and extracts
    the edges_to_id_mapping.

    Args:
        module_path: The module path to search from (e.g., "workflows.my_workflow")

    Returns:
        Dictionary mapping edge keys to their UUID strings
    """
    workflow_root, data = _load_workflow_metadata(module_path)
    if data is None:
        return None, {}
    edges_map = data.get("edges_to_id_mapping")
    if isinstance(edges_map, dict):
        return workflow_root, edges_map
    return workflow_root, {}


def load_edges_to_id_mapping(module_path: str) -> Dict[str, str]:
    _, mapping = _load_edges_mapping(module_path)
    return mapping


def _build_metadata_class_path(module: str, class_name: str, workflow_root: Optional[str]) -> str:
    """
    Format a class path so that it matches the metadata.json key structure.
    """
    if workflow_root:
        if module == workflow_root:
            return f".{class_name}"
        prefix = f"{workflow_root}."
        if module.startswith(prefix):
            relative = module[len(prefix) :]
            return f".{relative}.{class_name}" if relative else f".{class_name}"
    return f"{module}.{class_name}"


def get_trigger_edge_id(trigger_cls: Type, target_node: Type[BaseNode], module_path: str) -> Optional[str]:
    """
    Get the stable edge ID for a trigger edge from metadata.json.

    Args:
        trigger_cls: The trigger class
        target_node: The target node class
        module_path: The workflow module path

    Returns:
        The stable edge ID if found in metadata.json, None otherwise
    """
    workflow_root, edges_mapping = _load_edges_mapping(module_path)
    if not edges_mapping:
        return None
    trigger_path = _build_metadata_class_path(trigger_cls.__module__, trigger_cls.__name__, workflow_root)
    target_base = _build_metadata_class_path(target_node.__module__, target_node.__name__, workflow_root)
    target_path = f"{target_base}.Trigger"
    edge_key = f"{trigger_path}|{target_path}"
    return edges_mapping.get(edge_key)


def get_entrypoint_edge_id(target_node: Type[BaseNode], module_path: str) -> Optional[str]:
    """
    Get the stable edge ID for an entrypoint edge from metadata.json.

    Args:
        target_node: The target node class
        module_path: The workflow module path

    Returns:
        The stable edge ID if found in metadata.json, None otherwise
    """
    workflow_root, edges_mapping = _load_edges_mapping(module_path)
    if not edges_mapping:
        return None
    manual_path = "vellum.workflows.triggers.manual.Manual"
    target_base = _build_metadata_class_path(target_node.__module__, target_node.__name__, workflow_root)
    target_path = f"{target_base}.Trigger"
    edge_key = f"{manual_path}|{target_path}"
    return edges_mapping.get(edge_key)


def get_regular_edge_id(
    source_node_cls: Type[BaseNode], source_handle_id: UUID, target_node: Type[BaseNode], module_path: str
) -> Optional[str]:
    """
    Get the stable edge ID for a regular node-to-node edge from metadata.json.

    Args:
        source_node_cls: The source node class
        source_handle_id: The source port/handle ID
        target_node: The target node class
        module_path: The workflow module path

    Returns:
        The stable edge ID if found in metadata.json, None otherwise
    """
    workflow_root, edges_mapping = _load_edges_mapping(module_path)
    if not edges_mapping:
        return None
    source_base = _build_metadata_class_path(source_node_cls.__module__, source_node_cls.__name__, workflow_root)
    source_path = f"{source_base}.Ports.{str(source_handle_id)}"
    target_base = _build_metadata_class_path(target_node.__module__, target_node.__name__, workflow_root)
    target_path = f"{target_base}.Trigger"
    edge_key = f"{source_path}|{target_path}"
    return edges_mapping.get(edge_key)


def load_dataset_row_index_to_id_mapping(module_path: str) -> Dict[int, str]:
    """
    Load dataset row index to ID mapping from metadata.json for a given module.

    This function searches up the module hierarchy for metadata.json and extracts
    the dataset_row_index_to_id_mapping.

    Args:
        module_path: The module path to search from (e.g., "workflows.my_workflow")

    Returns:
        Dictionary mapping dataset row indices (as integers) to their ID strings
    """
    _, data = _load_workflow_metadata(module_path)
    if data is None:
        return {}
    mapping = data.get("dataset_row_index_to_id_mapping")
    if isinstance(mapping, dict):
        return {int(k): v for k, v in mapping.items()}
    return {}


def load_runner_config(module_path: str) -> Dict[str, Any]:
    """
    Load runner_config from metadata.json for a given module.

    This function searches up the module hierarchy for metadata.json and extracts
    the runner_config.

    Args:
        module_path: The module path to search from (e.g., "workflows.my_workflow")

    Returns:
        The runner_config dictionary if found in metadata.json, empty dict otherwise
    """
    _, data = _load_workflow_metadata(module_path)
    if data is None:
        return {}
    runner_config = data.get("runner_config")
    if isinstance(runner_config, dict):
        return runner_config
    return {}
