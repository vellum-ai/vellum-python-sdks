from uuid import UUID
from typing import Generic, Optional, TypeVar

from vellum.workflows.nodes.core.templating_node import TemplatingNode
from vellum.workflows.types.core import JsonObject
from vellum.workflows.utils.vellum_variables import primitive_type_to_vellum_variable_type
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_TemplatingNodeType = TypeVar("_TemplatingNodeType", bound=TemplatingNode)

TEMPLATE_INPUT_NAME = TemplatingNode.template.name


class BaseTemplatingNodeDisplay(BaseNodeVellumDisplay[_TemplatingNodeType], Generic[_TemplatingNodeType]):
    def serialize(
        self, display_context: WorkflowDisplayContext, error_output_id: Optional[UUID] = None, **kwargs
    ) -> JsonObject:
        node = self._node
        node_id = self.node_id

        template_input_id = self.node_input_ids_by_name.get(TEMPLATE_INPUT_NAME)

        template_node_input = create_node_input(
            node_id=node_id,
            input_name=TEMPLATE_INPUT_NAME,
            value=node.template,
            display_context=display_context,
            input_id=template_input_id,
        )
        template_node_inputs = raise_if_descriptor(node.inputs)
        template_inputs = [
            create_node_input(
                node_id=node_id,
                input_name=variable_name,
                value=variable_value,
                display_context=display_context,
                input_id=self.node_input_ids_by_name.get(f"{TemplatingNode.inputs.name}.{variable_name}")
                or self.node_input_ids_by_name.get(variable_name),
            )
            for variable_name, variable_value in template_node_inputs.items()
            if variable_name != TEMPLATE_INPUT_NAME
        ]
        node_inputs = [template_node_input, *template_inputs]

        # Misc type ignore is due to `node.Outputs` being generic
        # https://app.shortcut.com/vellum/story/4784
        output_descriptor = node.Outputs.result  # type: ignore [misc]
        _, output_display = display_context.global_node_output_displays[output_descriptor]
        inferred_output_type = primitive_type_to_vellum_variable_type(output_descriptor)

        return {
            "id": str(node_id),
            "type": "TEMPLATING",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "output_id": str(output_display.id),
                "error_output_id": str(error_output_id) if error_output_id else None,
                "source_handle_id": str(self.get_source_handle_id(display_context.port_displays)),
                "target_handle_id": str(self.get_target_handle_id()),
                "template_node_input_id": str(template_node_input.id),
                "output_type": inferred_output_type,
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
        }
