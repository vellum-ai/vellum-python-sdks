"""Utilities for reading and managing workflow metadata.json files."""

import json
import os
from uuid import UUID
from typing import Dict, Optional, Type

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


def load_edges_to_id_mapping(module_path: str) -> Dict[str, str]:
    """
    Load edge path to ID mapping from metadata.json for a given module.

    This function searches up the module hierarchy for metadata.json and extracts
    the edges_to_id_mapping.

    Args:
        module_path: The module path to search from (e.g., "workflows.my_workflow")

    Returns:
        Dictionary mapping edge keys to their UUID strings
    """
    try:
        root = find_workflow_root_with_metadata(module_path)
        if not root:
            return {}
        file_path = os.path.join(root.replace(".", os.path.sep), "metadata.json")
        with virtual_open(file_path) as f:
            data = json.load(f)
            edges_map = data.get("edges_to_id_mapping")
            return edges_map if isinstance(edges_map, dict) else {}
    except Exception:
        return {}


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
    edges_mapping = load_edges_to_id_mapping(module_path)
    trigger_path = f"{trigger_cls.__module__}.{trigger_cls.__name__}"
    target_path = f"{target_node.__module__}.{target_node.__name__}.Trigger"
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
    edges_mapping = load_edges_to_id_mapping(module_path)
    manual_path = "vellum.workflows.triggers.manual.Manual"
    target_path = f"{target_node.__module__}.{target_node.__name__}.Trigger"
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
    edges_mapping = load_edges_to_id_mapping(module_path)
    source_path = f"{source_node_cls.__module__}.{source_node_cls.__name__}.Ports.{str(source_handle_id)}"
    target_path = f"{target_node.__module__}.{target_node.__name__}.Trigger"
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
    try:
        root = find_workflow_root_with_metadata(module_path)
        if not root:
            return {}
        file_path = os.path.join(root.replace(".", os.path.sep), "metadata.json")
        with virtual_open(file_path) as f:
            data = json.load(f)
            mapping = data.get("dataset_row_index_to_id_mapping")
            if isinstance(mapping, dict):
                return {int(k): v for k, v in mapping.items()}
            return {}
    except Exception:
        return {}
