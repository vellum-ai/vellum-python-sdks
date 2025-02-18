from typing import Any, Generic, TypeVar

from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.types.core import JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_BaseAdornmentNodeType = TypeVar("_BaseAdornmentNodeType", bound=BaseAdornmentNode)


class BaseAdornmentNodeDisplay(BaseNodeVellumDisplay[_BaseAdornmentNodeType], Generic[_BaseAdornmentNodeType]):
    def serialize(self, display_context: WorkflowDisplayContext, adornment: JsonObject, **kwargs: Any) -> dict:
        wrapped_node = self._node.__wrapped_node__
        wrapped_node_display_class = get_node_display_class(BaseNodeDisplay, wrapped_node)
        wrapped_node_display = wrapped_node_display_class()
        serialized_wrapped_node = wrapped_node_display.serialize(display_context)

        adornments = serialized_wrapped_node.get("adornments") or []
        serialized_wrapped_node["adornments"] = adornments + [adornment]

        return serialized_wrapped_node
