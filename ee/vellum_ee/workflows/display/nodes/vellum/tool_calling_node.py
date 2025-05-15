from typing import Any, Generic, List, TypeVar

from vellum.workflows.nodes.experimental.tool_calling_node.node import ToolCallingNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.vellum import NodeInput

_ToolCallingNodeType = TypeVar("_ToolCallingNodeType", bound=ToolCallingNode)


class BaseToolCallingNodeDisplay(BaseNodeDisplay[_ToolCallingNodeType], Generic[_ToolCallingNodeType]):
    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        serialized_node = super().serialize(display_context, **kwargs)

        node = self._node
        node_id = self.node_id

        value = raise_if_descriptor(node.prompt_inputs)
        node_inputs: List[NodeInput] = []
        if value:
            for variable_name, variable_value in value.items():
                node_input = create_node_input(
                    node_id=node_id,
                    input_name=variable_name,
                    value=variable_value,
                    display_context=display_context,
                    input_id=self.node_input_ids_by_name.get(f"{ToolCallingNode.prompt_inputs.name}.{variable_name}")
                    or self.node_input_ids_by_name.get(variable_name),
                )
                node_inputs.append(node_input)

        return {
            "inputs": [node_input.dict() for node_input in node_inputs],
            **serialized_node,
        }
