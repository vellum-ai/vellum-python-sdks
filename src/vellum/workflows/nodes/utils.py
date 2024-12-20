from functools import cache
from typing import Type

from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports.port import Port
from vellum.workflows.types.generics import NodeType

ADORNMENT_MODULE_NAME = "<adornment>"


@cache
def get_unadorned_node(node: Type[BaseNode]) -> Type[BaseNode]:
    wrapped_node = getattr(node, "__wrapped_node__", None)
    if wrapped_node is not None:
        return get_unadorned_node(wrapped_node)

    return node


@cache
def get_unadorned_port(port: Port) -> Port:
    unadorned_node = get_unadorned_node(port.node_class)
    if unadorned_node == port.node_class:
        return port

    return getattr(unadorned_node.Ports, port.name)


@cache
def get_wrapped_node(node: Type[NodeType]) -> Type[BaseNode]:
    wrapped_node = getattr(node, "__wrapped_node__", None)
    if wrapped_node is None:
        raise AttributeError("Wrapped node not found")

    return wrapped_node


def has_wrapped_node(node: Type[NodeType]) -> bool:
    try:
        get_wrapped_node(node)
    except AttributeError:
        return False

    return True
