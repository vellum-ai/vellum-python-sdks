import json
import logging
import os
from typing import Any, Dict, List, Optional, Type

from vellum.workflows.nodes.bases.base import BaseNode
import vellum.workflows.nodes.displayable as displayable_module
from vellum.workflows.vellum_client import create_vellum_client
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import WorkflowDisplayContext

logger = logging.getLogger(__name__)


def create_display_context_with_client() -> WorkflowDisplayContext:
    """Create a WorkflowDisplayContext with Vellum client for serialization."""
    client = create_vellum_client()
    return WorkflowDisplayContext(client=client, dry_run=True)


def get_all_displayable_node_classes() -> List[Type[BaseNode]]:
    """Get all displayable node classes dynamically from the displayable module."""
    node_classes = []
    for class_name in displayable_module.__all__:
        node_class = getattr(displayable_module, class_name)
        node_classes.append(node_class)
    return node_classes


def clean_node_definition(definition: Dict[str, Any]) -> Dict[str, Any]:
    """Remove unwanted fields from a successfully serialized node definition."""
    fields_to_remove = ["inputs", "data", "type", "adornments", "should_file_merge"]
    cleaned = {k: v for k, v in definition.items() if k not in fields_to_remove}
    return cleaned


def serialize_node_definition(
    node_class: Type[BaseNode], display_context: WorkflowDisplayContext
) -> Optional[Dict[str, Any]]:
    """Serialize a single node definition, returning None if it fails."""
    try:
        display_class = get_node_display_class(node_class)
        display_instance = display_class()
        definition = display_instance.serialize(display_context)
        return clean_node_definition(definition)
    except Exception as e:
        logger.info(f"Warning: Failed to serialize {node_class.__name__}: {e}")
        return None


def main() -> None:
    """Main function to generate node definitions."""
    logger.info("Generating node definitions...")

    display_context = create_display_context_with_client()
    node_classes = get_all_displayable_node_classes()

    successful_nodes = []
    errors = []

    for node_class in node_classes:
        logger.info(f"Serializing {node_class.__name__}...")
        definition = serialize_node_definition(node_class, display_context)

        if definition is not None:
            successful_nodes.append(definition)
        else:
            try:
                display_class = get_node_display_class(node_class)
                display_instance = display_class()
                display_instance.serialize(display_context)
            except Exception as e:
                errors.append({"node": node_class.__name__, "error": f"{e.__class__.__name__}: {str(e)}"})

    result = {"nodes": successful_nodes, "errors": errors}

    output_path = "ee/vellum_ee/assets/node-definitions.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    logger.info(
        f"Generated {len(successful_nodes)} successful node definitions and {len(errors)} errors in {output_path}"
    )


if __name__ == "__main__":
    main()
