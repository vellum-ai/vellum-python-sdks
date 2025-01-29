import types
from typing import TYPE_CHECKING, Optional, Type

from vellum.workflows.types.generics import NodeType

if TYPE_CHECKING:
    from vellum_ee.workflows.display.types import NodeDisplayType


def get_node_display_class(
    base_class: Type["NodeDisplayType"], node_class: Type[NodeType], root_node_class: Optional[Type[NodeType]] = None
) -> Type["NodeDisplayType"]:
    node_display_class = base_class.get_from_node_display_registry(node_class)
    if node_display_class:
        if not issubclass(node_display_class, base_class):
            raise TypeError(
                f"Expected to find a subclass of '{base_class.__name__}' for node class '{node_class.__name__}'"
            )

        return node_display_class

    base_node_display_class = get_node_display_class(
        base_class, node_class.__bases__[0], node_class if root_node_class is None else root_node_class
    )

    # `base_node_display_class` is always a Generic class, so it's safe to index into it
    NodeDisplayBaseClass = base_node_display_class[node_class]  # type: ignore[index]
    NodeDisplayClass = types.new_class(
        f"{node_class.__name__}Display",
        bases=(NodeDisplayBaseClass,),
    )
    return NodeDisplayClass
