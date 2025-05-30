from uuid import UUID
from typing import Generic, Optional, TypeVar, cast

from vellum.workflows.nodes import MapNode
from vellum.workflows.types.core import JsonObject
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.base_adornment_node import BaseAdornmentNodeDisplay
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

_MapNodeType = TypeVar("_MapNodeType", bound=MapNode)


class BaseMapNodeDisplay(BaseAdornmentNodeDisplay[_MapNodeType], Generic[_MapNodeType]):
    __serializable_inputs__ = {MapNode.items}  # type: ignore[misc]

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        subworkflow = cast(type[BaseWorkflow], raise_if_descriptor(node.subworkflow))

        items_node_input = create_node_input(
            node_id=node_id,
            input_name="items",
            value=node.items,
            display_context=display_context,
            input_id=self.node_input_ids_by_name.get("items"),
        )
        node_inputs = [items_node_input]

        subworkflow_display = get_workflow_display(
            base_display_class=display_context.workflow_display_class,
            workflow_class=subworkflow,
            parent_display_context=display_context,
        )
        serialized_subworkflow = subworkflow_display.serialize()
        if not isinstance(serialized_subworkflow["input_variables"], list):
            raise ValueError("input_variables must be a list")

        input_variables = serialized_subworkflow["input_variables"]

        # Note: This must match the items input ID for the map node's node input
        items_workflow_input_id = next(
            input_variable["id"]
            for input_variable in input_variables
            if isinstance(input_variable, dict) and input_variable["key"] == "items"
        )
        item_workflow_input_id = next(
            input_variable["id"]
            for input_variable in input_variables
            if isinstance(input_variable, dict) and input_variable["key"] == "item"
        )
        index_workflow_input_id = next(
            input_variable["id"]
            for input_variable in input_variables
            if isinstance(input_variable, dict) and input_variable["key"] == "index"
        )

        return {
            "id": str(node_id),
            "type": "MAP",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "error_output_id": str(error_output_id) if error_output_id else None,
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "variant": "INLINE",
                "workflow_raw_data": serialized_subworkflow["workflow_raw_data"],
                "input_variables": cast(JsonObject, input_variables),
                "output_variables": serialized_subworkflow["output_variables"],
                "concurrency": raise_if_descriptor(node.max_concurrency),
                "items_input_id": items_workflow_input_id,
                "item_input_id": item_workflow_input_id,
                "index_input_id": index_workflow_input_id,
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
            "ports": self.serialize_ports(display_context),
        }
