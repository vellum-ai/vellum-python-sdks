from dataclasses import dataclass, field
from uuid import UUID
from typing import TYPE_CHECKING, Dict, Generic, Tuple, Type, TypeVar

from vellum.client.core import UniversalBaseModel
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference, WorkflowInputReference
from vellum_ee.workflows.display.base import (
    EdgeDisplayType,
    EntrypointDisplayType,
    WorkflowInputsDisplayType,
    WorkflowMetaDisplayType,
    WorkflowOutputDisplayType,
)
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay

if TYPE_CHECKING:
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
    from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

NodeDisplayType = TypeVar("NodeDisplayType", bound="BaseNodeDisplay")
WorkflowDisplayType = TypeVar("WorkflowDisplayType", bound="BaseWorkflowDisplay")


class NodeDisplay(UniversalBaseModel):
    input_display: Dict[str, UUID]
    output_display: Dict[str, UUID]
    port_display: Dict[str, UUID]


class WorkflowEventDisplayContext(UniversalBaseModel):
    node_displays: Dict[str, NodeDisplay]
    workflow_inputs: Dict[str, UUID]
    workflow_outputs: Dict[str, UUID]


@dataclass
class WorkflowDisplayContext(
    Generic[
        WorkflowMetaDisplayType,
        WorkflowInputsDisplayType,
        NodeDisplayType,
        EntrypointDisplayType,
        WorkflowOutputDisplayType,
        EdgeDisplayType,
    ]
):
    workflow_display_class: Type["BaseWorkflowDisplay"]
    workflow_display: WorkflowMetaDisplayType
    workflow_input_displays: Dict[WorkflowInputReference, WorkflowInputsDisplayType] = field(default_factory=dict)
    global_workflow_input_displays: Dict[WorkflowInputReference, WorkflowInputsDisplayType] = field(
        default_factory=dict
    )
    node_displays: Dict[Type[BaseNode], "NodeDisplayType"] = field(default_factory=dict)
    global_node_displays: Dict[Type[BaseNode], NodeDisplayType] = field(default_factory=dict)
    global_node_output_displays: Dict[OutputReference, Tuple[Type[BaseNode], "NodeOutputDisplay"]] = field(
        default_factory=dict
    )
    entrypoint_displays: Dict[Type[BaseNode], EntrypointDisplayType] = field(default_factory=dict)
    workflow_output_displays: Dict[BaseDescriptor, WorkflowOutputDisplayType] = field(default_factory=dict)
    edge_displays: Dict[Tuple[Port, Type[BaseNode]], EdgeDisplayType] = field(default_factory=dict)
    port_displays: Dict[Port, "PortDisplay"] = field(default_factory=dict)

    def build_event_display_context(self) -> WorkflowEventDisplayContext:
        workflow_outputs = {
            output.name: self.workflow_output_displays[output].id for output in self.workflow_output_displays
        }
        workflow_inputs = {input.name: self.workflow_input_displays[input].id for input in self.workflow_input_displays}
        node_displays = {str(node.__id__): self.node_displays[node] for node in self.node_displays}
        temp_node_displays = {}
        for node in node_displays:
            current_node = node_displays[node]
            input_display = {}
            if issubclass(current_node.__class__, BaseNodeVellumDisplay):
                input_display = current_node.node_input_ids_by_name  # type: ignore[attr-defined]
            node_display_meta = {
                output.name: current_node.output_display[output].id for output in current_node.output_display
            }
            port_display_meta = {port.name: current_node.port_displays[port].id for port in current_node.port_displays}

            temp_node_displays[node] = NodeDisplay(
                input_display=input_display,
                output_display=node_display_meta,
                port_display=port_display_meta,
            )
        display_meta = WorkflowEventDisplayContext(
            workflow_outputs=workflow_outputs,
            workflow_inputs=workflow_inputs,
            node_displays=temp_node_displays,
        )
        return display_meta
