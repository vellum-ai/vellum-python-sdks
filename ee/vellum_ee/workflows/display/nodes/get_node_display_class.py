import types
from typing import TYPE_CHECKING, Generic, Type, TypeVar

from vellum.workflows.types.generics import NodeType
from vellum_ee.workflows.display.utils.registry import get_from_node_display_registry

if TYPE_CHECKING:
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay


def get_node_display_class(node_class: Type[NodeType]) -> Type["BaseNodeDisplay"]:
    node_display_class = get_from_node_display_registry(node_class)
    if node_display_class:
        return node_display_class

    base_node_display_class = get_node_display_class(node_class.__bases__[0])

    # mypy gets upset at dynamic TypeVar's, but it's technically allowed by python
    _NodeClassType = TypeVar(f"_{node_class.__name__}Type", bound=node_class)  # type: ignore[misc]
    # `base_node_display_class` is always a Generic class, so it's safe to index into it
    NodeDisplayBaseClass = base_node_display_class[_NodeClassType]  # type: ignore[index]

    NodeDisplayClass = types.new_class(
        f"{node_class.__name__}Display",
        bases=(NodeDisplayBaseClass, Generic[_NodeClassType]),
    )

    return NodeDisplayClass
