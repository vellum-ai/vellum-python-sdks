from uuid import UUID
from typing import Any, Callable, Generic, Optional, TypeVar, cast

from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.nodes.utils import get_wrapped_node
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_BaseAdornmentNodeType = TypeVar("_BaseAdornmentNodeType", bound=BaseAdornmentNode)


class BaseAdornmentNodeDisplay(BaseNodeVellumDisplay[_BaseAdornmentNodeType], Generic[_BaseAdornmentNodeType]):
    def serialize(
        self,
        display_context: "WorkflowDisplayContext",
        **kwargs: Any,
    ) -> dict:
        node = self._node
        adornment = cast(Optional[JsonObject], kwargs.get("adornment"))
        get_additional_kwargs = cast(Optional[Callable[[UUID], dict]], kwargs.get("get_additional_kwargs"))

        wrapped_node = get_wrapped_node(node)
        if not wrapped_node:
            raise NotImplementedError(
                "Unable to serialize standalone adornment nodes. Please use adornment nodes as a decorator."
            )

        wrapped_node_display_class = get_node_display_class(BaseNodeDisplay, wrapped_node)
        wrapped_node_display = wrapped_node_display_class()
        additional_kwargs = get_additional_kwargs(wrapped_node_display.node_id) if get_additional_kwargs else {}
        serialized_wrapped_node = wrapped_node_display.serialize(display_context, **kwargs, **additional_kwargs)

        adornments = cast(JsonArray, serialized_wrapped_node.get("adornments")) or []
        serialized_wrapped_node["adornments"] = adornments + [adornment] if adornment else adornments

        return serialized_wrapped_node
