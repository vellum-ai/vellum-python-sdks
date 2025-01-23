from functools import cache
import sys
from types import ModuleType
from typing import Any, Callable, Optional, Type, TypeVar

from vellum.workflows.nodes import BaseNode
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.ports.port import Port
from vellum.workflows.types.generics import NodeType

ADORNMENT_MODULE_NAME = "<adornment>"


@cache
def get_unadorned_node(node: Type[BaseNode]) -> Type[BaseNode]:
    wrapped_node = get_wrapped_node(node)
    if wrapped_node is not None:
        return get_unadorned_node(wrapped_node)

    return node


@cache
def get_unadorned_port(port: Port) -> Port:
    unadorned_node = get_unadorned_node(port.node_class)
    if unadorned_node == port.node_class:
        return port

    return getattr(unadorned_node.Ports, port.name)


def get_wrapped_node(node: Type[NodeType]) -> Optional[Type[BaseNode]]:
    if not issubclass(node, BaseAdornmentNode):
        return None

    return node.__wrapped_node__


AdornableNode = TypeVar("AdornableNode", bound=BaseNode)


def create_adornment(
    adornable_cls: Type[AdornableNode], attributes: Optional[dict[str, Any]] = None
) -> Callable[..., Type["AdornableNode"]]:
    def decorator(inner_cls: Type[BaseNode]) -> Type["AdornableNode"]:
        # Investigate how to use dependency injection to avoid circular imports
        # https://app.shortcut.com/vellum/story/4116
        from vellum.workflows import BaseWorkflow

        class Subworkflow(BaseWorkflow):
            graph = inner_cls

            # mypy is wrong here, this works and is defined
            class Outputs(inner_cls.Outputs):  # type: ignore[name-defined]
                pass

        dynamic_module = f"{inner_cls.__module__}.{inner_cls.__name__}.{ADORNMENT_MODULE_NAME}"
        # This dynamic module allows calls to `type_hints` to work
        sys.modules[dynamic_module] = ModuleType(dynamic_module)

        # We use a dynamic wrapped node class to be uniquely tied to this `inner_cls` node during serialization
        WrappedNode = type(
            adornable_cls.__name__,
            (adornable_cls,),
            {
                "__wrapped_node__": inner_cls,
                "__module__": dynamic_module,
                "subworkflow": Subworkflow,
                "Ports": type("Ports", (adornable_cls.Ports,), {port.name: port.copy() for port in inner_cls.Ports}),
                **(attributes or {}),
            },
        )
        return WrappedNode

    return decorator
