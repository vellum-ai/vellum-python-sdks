from typing import Any, Generic, TypeVar

from vellum.workflows.nodes.experimental.tool_calling_node.node import ToolCallingNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_ToolCallingNodeType = TypeVar("_ToolCallingNodeType", bound=ToolCallingNode)


class BaseToolCallingNodeDisplay(BaseNodeDisplay[_ToolCallingNodeType], Generic[_ToolCallingNodeType]):
    def serialize(self, display_context: WorkflowDisplayContext, **kwargs: Any) -> JsonObject:
        serialized_node = super().serialize(display_context, **kwargs)
        return serialized_node
