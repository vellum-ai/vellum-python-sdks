import types
from uuid import UUID
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.types.generics import NodeType
from vellum.workflows.utils.uuids import uuid4_from_hash

if TYPE_CHECKING:
    from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay


def get_node_display_class(
    base_class: Type["BaseNodeDisplay"], node_class: Type[NodeType], root_node_class: Optional[Type[NodeType]] = None
) -> Type["BaseNodeDisplay"]:
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

    def _get_node_input_ids_by_ref(path: str, inst: Any):
        if isinstance(inst, dict):
            node_input_ids_by_name: Dict[str, UUID] = {}
            for key, value in inst.items():
                node_input_ids_by_name.update(_get_node_input_ids_by_ref(f"{path}.{key}", value))
            return node_input_ids_by_name

        if isinstance(inst, BaseDescriptor):
            return {path: uuid4_from_hash(f"{node_class.__id__}|{path}")}

        return {}

    def exec_body(ns: Dict):
        node_input_ids_by_name: Dict[str, UUID] = {}
        for ref in node_class:
            node_input_ids_by_name.update(_get_node_input_ids_by_ref(ref.name, ref.instance))

        if node_input_ids_by_name:
            ns["node_input_ids_by_name"] = node_input_ids_by_name

    NodeDisplayClass = types.new_class(
        f"{node_class.__name__}Display",
        bases=(NodeDisplayBaseClass,),
        exec_body=exec_body,
    )

    return NodeDisplayClass
