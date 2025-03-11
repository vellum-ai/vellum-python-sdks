import re
import types
from uuid import UUID
from typing import Any, Callable, Generic, Optional, Type, TypeVar, cast

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.nodes.utils import get_wrapped_node
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.types.utils import get_original_base
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

    @classmethod
    def wrap(cls, **kwargs: Any) -> Callable[..., Type[BaseNodeDisplay]]:
        NodeDisplayType = TypeVar("NodeDisplayType", bound=BaseNodeDisplay)

        def decorator(inner_cls: Type[NodeDisplayType]) -> Type[NodeDisplayType]:
            node_class = inner_cls.infer_node_class()
            wrapped_node_class = cast(Type[BaseNode], node_class.__wrapped_node__)

            # `mypy` is wrong here, `cls` is indexable bc it's Generic
            BaseAdornmentDisplay = cls[node_class]  # type: ignore[index]
            AdornmentDisplay = types.new_class(
                re.sub(r"^Base", "", cls.__name__),
                bases=(BaseAdornmentDisplay,),
            )
            for key, kwarg in kwargs.items():
                setattr(AdornmentDisplay, key, kwarg)

            setattr(inner_cls, "__adorned_by__", AdornmentDisplay)

            # We must edit the node display class to use __wrapped_node__ everywhere it
            # references the adorned node class, which is three places:

            # 1. The node display class' parameterized type
            original_base_node_display = get_original_base(inner_cls)
            original_base_node_display.__args__ = (wrapped_node_class,)
            inner_cls._node_display_registry[wrapped_node_class] = inner_cls

            # 2. The node display class' output displays
            old_outputs = list(inner_cls.output_display.keys())
            for old_output in old_outputs:
                new_output = getattr(wrapped_node_class.Outputs, old_output.name)
                inner_cls.output_display[new_output] = inner_cls.output_display.pop(old_output)

            # 3. The node display class' port displays
            old_ports = list(inner_cls.port_displays.keys())
            for old_port in old_ports:
                new_port = getattr(wrapped_node_class.Ports, old_port.name)
                inner_cls.port_displays[new_port] = inner_cls.port_displays.pop(old_port)

            return inner_cls

        return decorator
