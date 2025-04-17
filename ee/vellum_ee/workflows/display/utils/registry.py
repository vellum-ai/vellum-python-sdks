from typing import TYPE_CHECKING, Dict, Optional, Type

from vellum.workflows.nodes import BaseNode

if TYPE_CHECKING:
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay


# Used to store the mapping between node types and their display classes
_node_display_registry: Dict[Type[BaseNode], Type["BaseNodeDisplay"]] = {}


def get_from_node_display_registry(node_class: Type[BaseNode]) -> Optional[Type["BaseNodeDisplay"]]:
    return _node_display_registry.get(node_class)


def register_node_display_class(node_class: Type[BaseNode], node_display_class: Type["BaseNodeDisplay"]) -> None:
    _node_display_registry[node_class] = node_display_class
