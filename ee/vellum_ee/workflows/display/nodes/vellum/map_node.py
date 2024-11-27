from uuid import UUID
from typing import Any, ClassVar, Dict, Generic, List, Optional, Type, TypeVar

from vellum import VellumVariable
from vellum.workflows.nodes import MapNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.utils.vellum import infer_vellum_variable_type
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

_MapNodeType = TypeVar("_MapNodeType", bound=MapNode)


class BaseMapNodeDisplay(BaseNodeVellumDisplay[_MapNodeType], Generic[_MapNodeType]):
    workflow_input_ids_by_name: ClassVar[Dict[str, UUID]] = {}

    def serialize(self, display_context: WorkflowDisplayContext) -> JsonObject:
        node = self._node
        node_id = self.node_id

        workflow_inputs: List[VellumVariable] = []
        subworkflow = raise_if_descriptor(node.subworkflow)
        for descriptor in subworkflow.get_inputs_class():
            # In WaC it's always 'all_items'
            # In Vellum it's always 'items'
            variable_name = descriptor.name if descriptor.name != "all_items" else "items"
            variable_id = str(
                self.workflow_input_ids_by_name.get(variable_name)
                or uuid4_from_hash(f"{self.node_id}|{variable_name}")
            )
            workflow_inputs.append(
                VellumVariable(
                    id=variable_id,
                    key=variable_name,
                    type=infer_vellum_variable_type(descriptor),
                )
            )

        items_workflow_input = next(input for input in workflow_inputs if input.key == "items")
        item_workflow_input = next(input for input in workflow_inputs if input.key == "item")
        index_workflow_input = next(input for input in workflow_inputs if input.key == "index")

        workflow_outputs = self._generate_workflow_outputs(node)

        items_node_input = create_node_input(
            node_id=node_id,
            input_name="items",
            value=node.items,
            display_context=display_context,
            input_id=UUID(items_workflow_input.id),
        )
        node_inputs = [items_node_input]

        subworkflow_display = get_workflow_display(
            base_display_class=display_context.workflow_display_class,
            workflow_class=subworkflow,
        )
        serialized_subworkflow = subworkflow_display.serialize()

        return {
            "id": str(node_id),
            "type": "MAP",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "error_output_id": None,
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "variant": "INLINE",
                "workflow_raw_data": serialized_subworkflow["workflow_raw_data"],
                "input_variables": [workflow_input.dict() for workflow_input in workflow_inputs],
                "output_variables": [workflow_output.dict() for workflow_output in workflow_outputs],
                "concurrency": raise_if_descriptor(node.concurrency),
                "items_input_id": str(items_workflow_input.id),
                "item_input_id": str(item_workflow_input.id),
                "index_input_id": str(index_workflow_input.id),
            },
            "display_data": self.get_display_data().dict(),
            "definition": self.get_definition().dict(),
        }

    def _generate_workflow_outputs(
        self,
        node: Type[MapNode],
    ) -> List[VellumVariable]:
        workflow_outputs: List[VellumVariable] = []
        for output_descriptor in raise_if_descriptor(node.subworkflow).Outputs:  # type: ignore[union-attr]
            node_output_display = self.get_node_output_display(output_descriptor)
            output_type = infer_vellum_variable_type(output_descriptor)
            workflow_outputs.append(
                VellumVariable(id=str(node_output_display.id), key=node_output_display.name, type=output_type)
            )

        return workflow_outputs
