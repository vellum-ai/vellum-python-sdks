from uuid import UUID
from typing import ClassVar, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from vellum import VellumVariable
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import InlineSubworkflowNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type
from vellum_ee.workflows.display.vellum import NodeInput
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

_InlineSubworkflowNodeType = TypeVar("_InlineSubworkflowNodeType", bound=InlineSubworkflowNode)


class BaseInlineSubworkflowNodeDisplay(
    BaseNodeVellumDisplay[_InlineSubworkflowNodeType], Generic[_InlineSubworkflowNodeType]
):
    workflow_input_ids_by_name: ClassVar[Dict[str, UUID]] = {}

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        node_inputs, workflow_inputs = self._generate_node_and_workflow_inputs(node_id, node, display_context)

        subworkflow_display = get_workflow_display(
            base_display_class=display_context.workflow_display_class,
            workflow_class=raise_if_descriptor(node.subworkflow),
            parent_display_context=display_context,
        )
        workflow_outputs = self._generate_workflow_outputs(node, subworkflow_display.display_context)
        serialized_subworkflow = subworkflow_display.serialize()

        return {
            "id": str(node_id),
            "type": "SUBWORKFLOW",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "error_output_id": str(error_output_id) if error_output_id else None,
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "variant": "INLINE",
                "workflow_raw_data": serialized_subworkflow["workflow_raw_data"],
                "input_variables": [workflow_input.dict() for workflow_input in workflow_inputs],
                "output_variables": [workflow_output.dict() for workflow_output in workflow_outputs],
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
        }

    def _generate_node_and_workflow_inputs(
        self,
        node_id: UUID,
        node: Type[InlineSubworkflowNode],
        display_context: WorkflowDisplayContext,
    ) -> Tuple[List[NodeInput], List[VellumVariable]]:
        subworkflow = raise_if_descriptor(node.subworkflow)
        subworkflow_inputs_class = subworkflow.get_inputs_class()
        subworkflow_inputs = raise_if_descriptor(node.subworkflow_inputs)

        if isinstance(subworkflow_inputs, BaseInputs):
            subworkflow_entries = [
                (variable_ref.name, variable_value) for variable_ref, variable_value in subworkflow_inputs
            ]
        elif isinstance(subworkflow_inputs, dict):
            subworkflow_entries = [
                (variable_name, variable_value) for variable_name, variable_value in subworkflow_inputs.items()
            ]
        else:
            subworkflow_entries = [
                (descriptor.name, getattr(subworkflow_inputs_class, descriptor.name))
                for descriptor in subworkflow_inputs_class
                if hasattr(subworkflow_inputs_class, descriptor.name)
            ]

        node_inputs = [
            create_node_input(
                node_id=node_id,
                input_name=variable_name,
                value=variable_value,
                display_context=display_context,
                input_id=self.workflow_input_ids_by_name.get(variable_name),
            )
            for variable_name, variable_value in subworkflow_entries
        ]
        node_inputs_by_key = {node_input.key: node_input for node_input in node_inputs}
        workflow_inputs = [
            VellumVariable(
                id=node_inputs_by_key[descriptor.name].id,
                key=descriptor.name,
                type=infer_vellum_variable_type(descriptor),
            )
            for descriptor in subworkflow_inputs_class
        ]

        return node_inputs, workflow_inputs

    def _generate_workflow_outputs(
        self,
        node: Type[InlineSubworkflowNode],
        display_context: WorkflowDisplayContext,
    ) -> List[VellumVariable]:
        workflow_outputs: List[VellumVariable] = []
        for output_descriptor in raise_if_descriptor(node.subworkflow).Outputs:  # type: ignore[union-attr]
            workflow_output_display = display_context.workflow_output_displays[output_descriptor]
            output_type = infer_vellum_variable_type(output_descriptor)
            workflow_outputs.append(
                VellumVariable(id=str(workflow_output_display.id), key=workflow_output_display.name, type=output_type)
            )

        return workflow_outputs
