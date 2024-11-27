from functools import cache
from typing import Type

from vellum.workflows.nodes import BaseNode
from vellum.workflows.references import NodeReference
from vellum.workflows.types.generics import NodeType

ADORNMENT_MODULE_NAME = "<adornment>"


@cache
def get_wrapped_node(node: Type[NodeType]) -> Type[BaseNode]:
    if hasattr(node, "subworkflow"):
        subworkflow = node.subworkflow
        if isinstance(subworkflow, NodeReference) and subworkflow.instance:
            graph = subworkflow.instance.graph
            if issubclass(graph, BaseNode):
                return graph

    raise TypeError("Wrapped subworkflow contains more than one node")


def has_wrapped_node(node: Type[NodeType]) -> bool:
    try:
        get_wrapped_node(node)
    except TypeError:
        return False

    return True
