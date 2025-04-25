from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Tuple, Type

from vellum.client import Vellum as VellumClient
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.events.workflow import WorkflowEventDisplayContext  # noqa: F401
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, StateValueReference, WorkflowInputReference
from vellum.workflows.vellum_client import create_vellum_client
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.base import (
    EdgeDisplay,
    EntrypointDisplay,
    StateValueDisplay,
    WorkflowInputsDisplay,
    WorkflowMetaDisplay,
    WorkflowOutputDisplay,
)
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay
from vellum_ee.workflows.display.utils.registry import get_default_workflow_display_class

if TYPE_CHECKING:
    from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay


WorkflowInputsDisplays = Dict[WorkflowInputReference, WorkflowInputsDisplay]
StateValueDisplays = Dict[StateValueReference, StateValueDisplay]
NodeDisplays = Dict[Type[BaseNode], BaseNodeDisplay]
NodeOutputDisplays = Dict[OutputReference, Tuple[Type[BaseNode], NodeOutputDisplay]]
EntrypointDisplays = Dict[Type[BaseNode], EntrypointDisplay]
WorkflowOutputDisplays = Dict[BaseDescriptor, WorkflowOutputDisplay]
EdgeDisplays = Dict[Tuple[Port, Type[BaseNode]], EdgeDisplay]
PortDisplays = Dict[Port, PortDisplay]


@dataclass
class WorkflowDisplayContext:
    client: VellumClient = field(default_factory=create_vellum_client)
    workflow_display_class: Type["BaseWorkflowDisplay"] = field(default_factory=get_default_workflow_display_class)
    workflow_display: WorkflowMetaDisplay = field(default_factory=lambda: WorkflowMetaDisplay.get_default(BaseWorkflow))
    workflow_input_displays: WorkflowInputsDisplays = field(default_factory=dict)
    global_workflow_input_displays: WorkflowInputsDisplays = field(default_factory=dict)
    state_value_displays: StateValueDisplays = field(default_factory=dict)
    global_state_value_displays: StateValueDisplays = field(default_factory=dict)
    node_displays: NodeDisplays = field(default_factory=dict)
    global_node_displays: NodeDisplays = field(default_factory=dict)
    global_node_output_displays: NodeOutputDisplays = field(default_factory=dict)
    entrypoint_displays: EntrypointDisplays = field(default_factory=dict)
    workflow_output_displays: WorkflowOutputDisplays = field(default_factory=dict)
    edge_displays: EdgeDisplays = field(default_factory=dict)
    port_displays: PortDisplays = field(default_factory=dict)
