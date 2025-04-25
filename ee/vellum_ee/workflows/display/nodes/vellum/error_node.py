from uuid import UUID
from typing import Any, ClassVar, Generic, Optional, TypeVar

from vellum.workflows.nodes import ErrorNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.utils import raise_if_descriptor
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_ErrorNodeType = TypeVar("_ErrorNodeType", bound=ErrorNode)
LEGACY_INPUT_NAME = "error_source_input_id"


class BaseErrorNodeDisplay(BaseNodeDisplay[_ErrorNodeType], Generic[_ErrorNodeType]):
    # DEPRECATED: Remove in 0.15.0 once removed from the vellum-side
    error_output_id: ClassVar[Optional[UUID]] = None
    # DEPRECATED: Remove in 0.15.0 once removed from the vellum-side
    name: ClassVar[Optional[str]] = None

    __serializable_inputs__ = {ErrorNode.error}

    def serialize(self, display_context: WorkflowDisplayContext, **kwargs) -> JsonObject:
        node_id = self.node_id
        error_source_input_id = self.node_input_ids_by_name.get(
            ErrorNode.error.name,
        ) or self.node_input_ids_by_name.get(LEGACY_INPUT_NAME)

        error_attribute = raise_if_descriptor(self._node.error)

        node_inputs = [
            create_node_input(
                node_id=node_id,
                input_name=LEGACY_INPUT_NAME,
                value=error_attribute,
                display_context=display_context,
                input_id=error_source_input_id,
            )
        ]

        node_data: dict[str, Any] = {
            "id": str(node_id),
            "type": "ERROR",
            "inputs": [node_input.dict() for node_input in node_inputs],
            "data": {
                "label": self.label,
                "target_handle_id": str(self.get_target_handle_id()),
                "error_source_input_id": str(error_source_input_id),
            },
            "display_data": self.get_display_data().dict(),
            "base": self.get_base().dict(),
            "definition": self.get_definition().dict(),
        }

        if self.name:
            node_data["data"]["name"] = self.name

        if self.error_output_id:
            node_data["data"]["error_output_id"] = str(self.error_output_id)

        return node_data
