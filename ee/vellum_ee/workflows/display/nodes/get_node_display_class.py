import types
from uuid import UUID
from typing import TYPE_CHECKING, Any, Dict, Generic, Type, TypeVar

from vellum.workflows.types.generics import NodeType
from vellum.workflows.utils.uuids import uuid4_from_hash
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

    def _get_node_input_ids_by_ref(path: str, inst: Any):
        if isinstance(inst, dict):
            node_input_ids_by_name: Dict[str, UUID] = {}
            for key, value in inst.items():
                node_input_ids_by_name.update(_get_node_input_ids_by_ref(f"{path}.{key}", value))
            return node_input_ids_by_name

        return {path: uuid4_from_hash(f"{node_class.__id__}|{path}")}

    def exec_body(ns: Dict):
        node_input_ids_by_name: Dict[str, UUID] = {}
        for ref in node_class:
            if ref not in base_node_display_class.__serializable_inputs__:
                continue

            node_input_ids_by_name.update(_get_node_input_ids_by_ref(ref.name, ref.instance))

        if node_input_ids_by_name:
            ns["node_input_ids_by_name"] = node_input_ids_by_name

    NodeDisplayClass = types.new_class(
        f"{node_class.__name__}Display",
        bases=(NodeDisplayBaseClass, Generic[_NodeClassType]),
        exec_body=exec_body,
    )

    return NodeDisplayClass
