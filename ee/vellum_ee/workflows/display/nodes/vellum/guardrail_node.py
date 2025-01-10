from uuid import UUID
from typing import ClassVar, Dict, Generic, Optional, TypeVar

from vellum.workflows.nodes import GuardrailNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_GuardrailNodeType = TypeVar("_GuardrailNodeType", bound=GuardrailNode)


class BaseGuardrailNodeDisplay(BaseNodeVellumDisplay[_GuardrailNodeType], Generic[_GuardrailNodeType]):
    metric_input_ids_by_name: ClassVar[Dict[str, UUID]] = {}

    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        metric_inputs = raise_if_descriptor(node.metric_inputs)
        node_inputs = [
            create_node_input(
                node_id=node_id,
                input_name=variable_name,
                value=variable_value,
                display_context=display_context,
                input_id=self.metric_input_ids_by_name.get(variable_name),
            )
            for variable_name, variable_value in metric_inputs.items()
        ]

        return {
            "id": str(node_id),
            "type": "METRIC",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "error_output_id": str(error_output_id) if error_output_id else None,
                "metric_definition_id": str(raise_if_descriptor(node.metric_definition)),
                "release_tag": raise_if_descriptor(node.release_tag),
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
        }
