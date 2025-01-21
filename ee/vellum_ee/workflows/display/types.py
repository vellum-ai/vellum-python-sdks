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

    def build_meta(self) -> WorkflowEventDisplayContext:
        # type ignores due to bound types mapping to values there
        workflow_outputs = {
            output.name: self.workflow_output_displays[output].id for output in self.workflow_output_displays
        }
        workflow_inputs = {input.name: self.workflow_input_displays[input].id for input in self.workflow_input_displays}
        node_displays = {str(node.__id__): self.node_displays[node] for node in self.node_displays}
        temp_node_displays = {}
        for node in node_displays:
            current_node = node_displays[node]
            outputs = current_node.output_display
            node_display_meta = {}
            for output in outputs:
                node_display_meta[output.name] = outputs[output].id
            ports = current_node.port_displays
            port_display_meta = {}
            for port in ports:
                port_display_meta[port.name] = ports[port].id

            temp_node_displays[node] = NodeDisplay(
                input_display=current_node.node_input_ids_by_name,  # type: ignore[attr-defined]
                output_display=node_display_meta,
                port_display=port_display_meta,
            )
        display_meta = WorkflowEventDisplayContext(
            workflow_outputs=workflow_outputs,
            workflow_inputs=workflow_inputs,
            node_displays=temp_node_displays,
        )
        return display_meta
