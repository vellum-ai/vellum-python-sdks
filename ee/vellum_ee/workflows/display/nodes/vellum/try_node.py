from uuid import UUID
from typing import Any, ClassVar, Generic, Optional, TypeVar

from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME, get_wrapped_node
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.uuids import uuid4_from_hash

_TryNodeType = TypeVar("_TryNodeType", bound=TryNode)


class BaseTryNodeDisplay(BaseNodeVellumDisplay[_TryNodeType], Generic[_TryNodeType]):
    error_output_id: ClassVar[Optional[UUID]] = None

    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        node = self._node

        try:
            inner_node = get_wrapped_node(node)
        except TypeError:
            raise NotImplementedError(
                "Unable to serialize Try Nodes that wrap subworkflows containing more than one Node."
            )

        # We need the node display class of the underlying node because
        # it contains the logic for serializing the node and potential display overrides
        node_display_class = get_node_display_class(BaseNodeVellumDisplay, inner_node)
        node_display = node_display_class(inner_node)

        serialized_node = node_display.serialize(display_context)

        serialized_node_data = serialized_node.get("data")
        if isinstance(serialized_node_data, dict):
            serialized_node_data["error_output_id"] = str(
                self.error_output_id or uuid4_from_hash(f"{node_display.node_id}|error_output_id")
            )

        serialized_node_definition = serialized_node.get("definition")
        if isinstance(serialized_node_definition, dict):
            serialized_node_definition_module = serialized_node_definition.get("module")
            if isinstance(serialized_node_definition_module, list):
                serialized_node_definition_module.extend(
                    [
                        serialized_node_definition["name"],
                        ADORNMENT_MODULE_NAME,
                    ]
                )
                serialized_node_definition["name"] = node.__name__

        return serialized_node
