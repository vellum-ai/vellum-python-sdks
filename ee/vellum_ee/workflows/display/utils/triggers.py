from typing import Any, Dict, List, Type, cast

from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.triggers.chat_message import ChatMessageTrigger
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.triggers.schedule import ScheduleTrigger
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.utils.vellum_variables import primitive_type_to_vellum_variable_type
from vellum_ee.workflows.display.base import WorkflowTriggerType
from vellum_ee.workflows.display.utils.vellum import compile_descriptor_annotation


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
        raise ValueError(
            f"Unknown trigger type: {trigger_class.__name__}. "
            f"Please add it to the trigger type mapping in get_trigger_type_mapping()."
        )


def serialize_trigger_attributes(trigger_class: Type[BaseTrigger]) -> JsonArray:
    """Serialize trigger attributes from attribute_references as VellumVariables."""
    attribute_references = trigger_class.attribute_references().values()

    def get_attribute_type(reference: Any) -> str:
        # We can remove this type ignore with some mypy plugin changes
        message_name = ChatMessageTrigger.message.name  # type: ignore[union-attr]
        # For ChatMessageTrigger.message, always return ARRAY to maintain backwards compatibility
        if issubclass(trigger_class, ChatMessageTrigger) and reference.name == message_name:
            return "ARRAY"
        try:
            return primitive_type_to_vellum_variable_type(reference)
        except ValueError:
            return "JSON"

    trigger_attributes: JsonArray = cast(
        JsonArray,
        [
            cast(
                JsonObject,
                {
                    "id": str(reference.id),
                    "key": reference.name,
                    "type": get_attribute_type(reference),
                    "required": type(None) not in reference.types,
                    "default": {
                        "type": get_attribute_type(reference),
                        "value": None,
                    },
                    "extensions": None,
                    "schema": compile_descriptor_annotation(reference),
                },
            )
            for reference in sorted(attribute_references, key=lambda ref: ref.name)
        ],
    )

    return trigger_attributes


def serialize_trigger_display_data(trigger_class: Type[BaseTrigger], trigger_type: WorkflowTriggerType) -> JsonObject:
    """Serialize display_data from trigger's Display class."""
    display_class = trigger_class.Display
    display_data: JsonObject = {}

    if hasattr(display_class, "label") and display_class.label is not None:
        display_data["label"] = display_class.label

    if (
        hasattr(display_class, "x")
        and display_class.x is not None
        and hasattr(display_class, "y")
        and display_class.y is not None
    ):
        display_data["position"] = {
            "x": display_class.x,
            "y": display_class.y,
        }

    if hasattr(display_class, "z_index") and display_class.z_index is not None:
        display_data["z_index"] = display_class.z_index

    if hasattr(display_class, "icon") and display_class.icon is not None:
        display_data["icon"] = display_class.icon

    if hasattr(display_class, "color") and display_class.color is not None:
        display_data["color"] = display_class.color

    if hasattr(display_class, "comment") and display_class.comment is not None:
        display_data["comment"] = {
            "value": display_class.comment.value,
            "expanded": display_class.comment.expanded,
        }

    return display_data


def serialize_trigger_definition(trigger_class: Type[BaseTrigger]) -> Dict[str, Any]:
    """
    Serialize a trigger class definition for use in node-definitions.json.

    This produces a simplified trigger definition that includes:
    - type: The WorkflowTriggerType enum value
    - name: The trigger class name
    - module: The module path as an array
    - attributes: The trigger's attribute references
    - display_data: Optional display metadata (label, icon, color)
    """
    trigger_type = get_trigger_type(trigger_class)

    definition: Dict[str, Any] = {
        "type": trigger_type.value,
        "name": trigger_class.__name__,
        "module": trigger_class.__module__.split("."),
        "attributes": serialize_trigger_attributes(trigger_class),
    }

    display_data = serialize_trigger_display_data(trigger_class, trigger_type)

    # Don't include display_data for manual triggers (consistent with workflow serialization)
    if display_data and trigger_type != WorkflowTriggerType.MANUAL:
        definition["display_data"] = display_data

    return definition


def get_all_trigger_classes() -> List[Type[BaseTrigger]]:
    """
    Get all trigger classes dynamically from the triggers module.

    This mirrors the approach used by get_all_displayable_node_classes for nodes.
    """
    import vellum.workflows.triggers as triggers_module

    trigger_classes = []
    for class_name in triggers_module.__all__:
        trigger_class = getattr(triggers_module, class_name)
        # Skip BaseTrigger itself - we only want concrete trigger types
        if trigger_class is BaseTrigger:
            continue
        if isinstance(trigger_class, type) and issubclass(trigger_class, BaseTrigger):
            trigger_classes.append(trigger_class)
    return trigger_classes
