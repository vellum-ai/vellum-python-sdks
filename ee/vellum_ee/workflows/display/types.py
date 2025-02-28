from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Generic, Tuple, Type, TypeVar

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.events.workflow import WorkflowEventDisplayContext  # noqa: F401
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, StateValueReference, WorkflowInputReference
from vellum_ee.workflows.display.base import (
    EdgeDisplayType,
    EntrypointDisplayType,
    StateValueDisplayType,
    WorkflowInputsDisplayType,
    WorkflowMetaDisplayType,
    WorkflowOutputDisplay,
)

if TYPE_CHECKING:
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
    from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay
    from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

NodeDisplayType = TypeVar("NodeDisplayType", bound="BaseNodeDisplay")
WorkflowDisplayType = TypeVar("WorkflowDisplayType", bound="BaseWorkflowDisplay")


@dataclass
class WorkflowDisplayContext(
    Generic[
        WorkflowMetaDisplayType,
        WorkflowInputsDisplayType,
        StateValueDisplayType,
        NodeDisplayType,
        EntrypointDisplayType,
        EdgeDisplayType,
    ]
):
    workflow_display_class: Type["BaseWorkflowDisplay"]
    workflow_display: WorkflowMetaDisplayType
    workflow_input_displays: Dict[WorkflowInputReference, WorkflowInputsDisplayType] = field(default_factory=dict)
    global_workflow_input_displays: Dict[WorkflowInputReference, WorkflowInputsDisplayType] = field(
        default_factory=dict
    )
    state_value_displays: Dict[StateValueReference, StateValueDisplayType] = field(default_factory=dict)
    global_state_value_displays: Dict[StateValueReference, StateValueDisplayType] = field(default_factory=dict)
    node_displays: Dict[Type[BaseNode], "NodeDisplayType"] = field(default_factory=dict)
    global_node_displays: Dict[Type[BaseNode], NodeDisplayType] = field(default_factory=dict)
    global_node_output_displays: Dict[OutputReference, Tuple[Type[BaseNode], "NodeOutputDisplay"]] = field(
        default_factory=dict
    )
    entrypoint_displays: Dict[Type[BaseNode], EntrypointDisplayType] = field(default_factory=dict)
    workflow_output_displays: Dict[BaseDescriptor, WorkflowOutputDisplay] = field(default_factory=dict)
    edge_displays: Dict[Tuple[Port, Type[BaseNode]], EdgeDisplayType] = field(default_factory=dict)
    port_displays: Dict[Port, "PortDisplay"] = field(default_factory=dict)
