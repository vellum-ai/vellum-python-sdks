import json
import logging
import os
from typing import Any, Dict, List, Optional, Type

from vellum.workflows.nodes.bases.base import BaseNode
import vellum.workflows.nodes.displayable as displayable_module
from vellum.workflows.triggers import (
    BaseTrigger,
    ChatMessageTrigger,
    IntegrationTrigger,
    ManualTrigger,
    ScheduleTrigger,
)
from vellum.workflows.vellum_client import create_vellum_client
from vellum_ee.workflows.display.base import WorkflowTriggerType
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


def get_all_trigger_classes() -> List[Type[BaseTrigger]]:
    """Get all trigger classes that should be included in definitions."""
    return [
        ManualTrigger,
        IntegrationTrigger,
        ScheduleTrigger,
        ChatMessageTrigger,
    ]


def get_trigger_type(trigger_class: Type[BaseTrigger]) -> WorkflowTriggerType:
    """Get the WorkflowTriggerType for a trigger class."""
    if issubclass(trigger_class, ManualTrigger):
        return WorkflowTriggerType.MANUAL
    elif issubclass(trigger_class, IntegrationTrigger):
        return WorkflowTriggerType.INTEGRATION
    elif issubclass(trigger_class, ScheduleTrigger):
        return WorkflowTriggerType.SCHEDULED
    elif issubclass(trigger_class, ChatMessageTrigger):
        return WorkflowTriggerType.CHAT_MESSAGE
    else:
        raise ValueError(f"Unknown trigger type: {trigger_class.__name__}")


def serialize_trigger_definition(trigger_class: Type[BaseTrigger]) -> Dict[str, Any]:
    """Serialize a single trigger definition."""
    trigger_type = get_trigger_type(trigger_class)

    definition: Dict[str, Any] = {
        "type": trigger_type.value,
        "name": trigger_class.__name__,
        "module": trigger_class.__module__.split("."),
    }

    display_class = trigger_class.Display
    display_data: Dict[str, Any] = {}

    if hasattr(display_class, "label") and display_class.label is not None:
        display_data["label"] = display_class.label

    if hasattr(display_class, "icon") and display_class.icon is not None:
        display_data["icon"] = display_class.icon

    if hasattr(display_class, "color") and display_class.color is not None:
        display_data["color"] = display_class.color

    if display_data:
        definition["display_data"] = display_data

    return definition


def main() -> None:
    """Main function to generate node and trigger definitions."""
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

    # Generate trigger definitions
    logger.info("Generating trigger definitions...")
    trigger_classes = get_all_trigger_classes()
    triggers = []

    for trigger_class in trigger_classes:
        logger.info(f"Serializing {trigger_class.__name__}...")
        trigger_definition = serialize_trigger_definition(trigger_class)
        triggers.append(trigger_definition)

    result = {"nodes": successful_nodes, "triggers": triggers, "errors": errors}

    output_path = "ee/vellum_ee/assets/node-definitions.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    logger.info(
        f"Generated {len(successful_nodes)} node definitions, {len(triggers)} trigger definitions, "
        f"and {len(errors)} errors in {output_path}"
    )


if __name__ == "__main__":
    main()
