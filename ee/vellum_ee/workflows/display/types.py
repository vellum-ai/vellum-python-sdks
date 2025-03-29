from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Generic, Tuple, Type, TypeVar

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.events.workflow import WorkflowEventDisplayContext  # noqa: F401
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, StateValueReference, WorkflowInputReference
from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    StateValueDisplay,
    WorkflowInputsDisplayType,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay

if TYPE_CHECKING:
    from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

WorkflowDisplayType = TypeVar("WorkflowDisplayType", bound="BaseWorkflowDisplay")

StateValueDisplays = Dict[StateValueReference, StateValueDisplay]
NodeDisplays = Dict[Type[BaseNode], BaseNodeDisplay]
NodeOutputDisplays = Dict[OutputReference, Tuple[Type[BaseNode], NodeOutputDisplay]]
EntrypointDisplays = Dict[Type[BaseNode], EntrypointDisplay]
WorkflowOutputDisplays = Dict[BaseDescriptor, WorkflowOutputDisplay]
EdgeDisplays = Dict[Tuple[Port, Type[BaseNode]], EdgeDisplay]
PortDisplays = Dict[Port, PortDisplay]


@dataclass
class WorkflowDisplayContext(Generic[WorkflowInputsDisplayType,]):
    workflow_display_class: Type["BaseWorkflowDisplay"]
    workflow_display: WorkflowMetaDisplay
    workflow_input_displays: Dict[WorkflowInputReference, WorkflowInputsDisplayType] = field(default_factory=dict)
    global_workflow_input_displays: Dict[WorkflowInputReference, WorkflowInputsDisplayType] = field(
        default_factory=dict
    )
    state_value_displays: StateValueDisplays = field(default_factory=dict)
    global_state_value_displays: StateValueDisplays = field(default_factory=dict)
    node_displays: NodeDisplays = field(default_factory=dict)
    global_node_displays: NodeDisplays = field(default_factory=dict)
    global_node_output_displays: NodeOutputDisplays = field(default_factory=dict)
    entrypoint_displays: EntrypointDisplays = field(default_factory=dict)
    workflow_output_displays: WorkflowOutputDisplays = field(default_factory=dict)
    edge_displays: EdgeDisplays = field(default_factory=dict)
    port_displays: PortDisplays = field(default_factory=dict)
