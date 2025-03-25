import re
import types
from uuid import UUID
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar, cast

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.nodes.utils import get_wrapped_node
from vellum.workflows.types.core import JsonArray, JsonObject
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.get_node_display_class import get_node_display_class
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.types import WorkflowDisplayContext

_BaseAdornmentNodeType = TypeVar("_BaseAdornmentNodeType", bound=BaseAdornmentNode)


def _recursively_replace_wrapped_node(node_class: Type[BaseNode], wrapped_node_display_class: Type["BaseNodeDisplay"]):
    if not issubclass(node_class, BaseAdornmentNode):
        return

    # We must edit the node display class to use __wrapped_node__ everywhere it
    # references the adorned node class, which is three places:
    wrapped_node_class = node_class.__wrapped_node__
    if not wrapped_node_class:
        raise ValueError(f"Node {node_class.__name__} must be used as an adornment with the `wrap` method.")

    # 1. The node display class' parameterized type
    original_base_node_display = get_original_base(wrapped_node_display_class)
    original_base_node_display.__args__ = (wrapped_node_class,)
    wrapped_node_display_class._node_display_registry[wrapped_node_class] = wrapped_node_display_class
    wrapped_node_display_class.__annotate_node__()

    # 2. The node display class' output displays
    for old_output in node_class.Outputs:
        new_output = getattr(wrapped_node_class.Outputs, old_output.name, None)
        if new_output is None:
            # If the adornment is adding a new output, such as TryNode adding an "error" output,
            # we skip it, since it should not be included in the adorned node's output displays
            wrapped_node_display_class.output_display.pop(old_output, None)
            continue

        if old_output not in wrapped_node_display_class.output_display:
            # If the adorned node doesn't have an output display defined for this output, we define one
            wrapped_node_display_class.output_display[new_output] = NodeOutputDisplay(
                id=wrapped_node_class.__output_ids__[old_output.name],
                name=old_output.name,
            )
        else:
            wrapped_node_display_class.output_display[new_output] = wrapped_node_display_class.output_display.pop(
                old_output
            )

    # 3. The node display class' port displays
    old_ports = list(wrapped_node_display_class.port_displays.keys())
    for old_port in old_ports:
        new_port = getattr(wrapped_node_class.Ports, old_port.name)
        wrapped_node_display_class.port_displays[new_port] = wrapped_node_display_class.port_displays.pop(old_port)

    # Now we keep drilling down recursively
    if (
        issubclass(wrapped_node_display_class, BaseAdornmentNodeDisplay)
        and wrapped_node_display_class.__wrapped_node_display__
    ):
        _recursively_replace_wrapped_node(
            wrapped_node_class,
            wrapped_node_display_class.__wrapped_node_display__,
        )


class BaseAdornmentNodeDisplay(BaseNodeVellumDisplay[_BaseAdornmentNodeType], Generic[_BaseAdornmentNodeType]):
    __wrapped_node_display__: Optional[Type[BaseNodeDisplay]] = None

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
    def wrap(cls, node_id: Optional[UUID] = None, **kwargs: Any) -> Callable[..., Type[BaseNodeDisplay]]:
        NodeDisplayType = TypeVar("NodeDisplayType", bound=BaseNodeDisplay)

        def decorator(wrapped_node_display_class: Type[NodeDisplayType]) -> Type[NodeDisplayType]:
            node_class = wrapped_node_display_class.infer_node_class()
            if not issubclass(node_class, BaseAdornmentNode):
                raise ValueError(f"Node {node_class.__name__} must be wrapped with a {BaseAdornmentNode.__name__}")

            # `mypy` is wrong here, `cls` is indexable bc it's Generic
            BaseAdornmentDisplay = cls[node_class]  # type: ignore[index]

            def exec_body(ns: Dict):
                for key, kwarg in kwargs.items():
                    ns[key] = kwarg

                ns["node_id"] = node_id or uuid4_from_hash(node_class.__qualname__)
                ns["__wrapped_node_display__"] = wrapped_node_display_class

            AdornmentDisplay = types.new_class(
                re.sub(r"^Base", "", cls.__name__), bases=(BaseAdornmentDisplay,), exec_body=exec_body
            )

            setattr(wrapped_node_display_class, "__adorned_by__", AdornmentDisplay)

            _recursively_replace_wrapped_node(
                node_class,
                wrapped_node_display_class,
            )

            return AdornmentDisplay

        return decorator
