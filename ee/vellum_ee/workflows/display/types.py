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
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay, PortDisplayOverrides

if TYPE_CHECKING:
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
    from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay

NodeDisplayType = TypeVar("NodeDisplayType", bound="BaseNodeDisplay")
WorkflowDisplayType = TypeVar("WorkflowDisplayType", bound="BaseWorkflowDisplay")


class OutputDisplay(UniversalBaseModel):
    id: UUID
    name: str
    label: str
    node_id: UUID
    node_input_id: UUID
    target_handle_id: UUID
    edge_id: UUID


class InputDisplay(UniversalBaseModel):
    id: UUID
    name: str
    required: bool


class NodeDisplay(UniversalBaseModel):
    input_display: Dict[str, UUID]
    output_display: Dict[str, NodeOutputDisplay]
    port_display: Dict[str, PortDisplayOverrides]


class WorkflowDisplayMeta(UniversalBaseModel):
    node_displays: Dict[str, NodeDisplay]
    workflow_inputs: Dict[str, InputDisplay]
    workflow_outputs: Dict[str, OutputDisplay]


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

    def build_meta(self) -> WorkflowDisplayMeta:
        # type ignores due to bound types mapping to values there
        workflow_outputs = {}
        for output in self.workflow_output_displays:
            current_output = self.workflow_output_displays[output]
            workflow_outputs[output.name] = OutputDisplay(
                id=current_output.id,  # type: ignore[attr-defined]
                name=current_output.name,  # type: ignore[attr-defined]
                label=current_output.label,  # type: ignore[attr-defined]
                node_id=current_output.node_id,  # type: ignore[attr-defined]
                node_input_id=current_output.node_input_id,  # type: ignore[attr-defined]
                target_handle_id=current_output.target_handle_id,  # type: ignore[attr-defined]
                edge_id=current_output.edge_id,  # type: ignore[attr-defined]
            )
        workflow_inputs = {}
        for input in self.workflow_input_displays:
            current_inputs = self.workflow_input_displays[input]
            workflow_inputs[input.name] = InputDisplay(
                id=current_inputs.id,
                name=current_inputs.name,  # type: ignore[attr-defined]
                required=current_inputs.required,  # type: ignore[attr-defined]
            )
        node_displays = {str(node.__id__): self.node_displays[node] for node in self.node_displays}
        temp_node_displays = {}
        for node in node_displays:
            current_node = node_displays[node]
            outputs = current_node.output_display
            node_display_meta = {}
            for output in outputs:
                node_display_meta[output.name] = outputs[output]
            ports = current_node.port_displays
            port_display_meta = {}
            for port in ports:
                port_display_meta[port.name] = ports[port]

            temp_node_displays[node] = NodeDisplay(
                input_display=current_node.node_input_ids_by_name,  # type: ignore[attr-defined]
                output_display=node_display_meta,
                port_display=port_display_meta,
            )
        display_meta = WorkflowDisplayMeta(
            workflow_outputs=workflow_outputs,
            workflow_inputs=workflow_inputs,
            node_displays=temp_node_displays,
        )
        return display_meta
