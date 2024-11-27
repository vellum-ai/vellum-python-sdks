from functools import cached_property
import inspect
from uuid import UUID
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Type, TypeVar, get_args

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.utils import get_wrapped_node, has_wrapped_node
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference
from vellum.workflows.types.core import JsonObject
from vellum.workflows.types.generics import NodeType
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.names import pascal_to_title_case
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay, PortDisplayOverrides
from vellum_ee.workflows.display.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.vellum import CodeResourceDefinition, NodeDefinition

if TYPE_CHECKING:
    from vellum_ee.workflows.display.types import WorkflowDisplayContext

_NodeDisplayAttrType = TypeVar("_NodeDisplayAttrType")


class BaseNodeDisplay(Generic[NodeType]):
    output_display: Dict[OutputReference, NodeOutputDisplay] = {}
    port_displays: Dict[Port, PortDisplayOverrides] = {}

    # Used to store the mapping between node types and their display classes
    _node_display_registry: Dict[Type[NodeType], Type["BaseNodeDisplay"]] = {}

    def __init__(self, node: Type[NodeType]):
        self._node = node

    def serialize(self, display_context: "WorkflowDisplayContext") -> JsonObject:
        raise NotImplementedError(f"Serialization for nodes of type {self._node.__name__} is not supported.")

    def get_definition(self) -> NodeDefinition:
        node = self._node
        node_definition = NodeDefinition(
            name=node.__name__,
            module=node.__module__.split("."),
            bases=[
                CodeResourceDefinition(
                    name=base.__name__,
                    module=base.__module__.split("."),
                )
                for base in node.__bases__
            ],
        )
        return node_definition

    def get_node_output_display(self, output: OutputReference) -> NodeOutputDisplay:
        explicit_display = self.output_display.get(output)
        if explicit_display:
            return explicit_display

        return NodeOutputDisplay(id=uuid4_from_hash(f"{self.node_id}|{output.name}"), name=output.name)

    def get_node_port_display(self, port: Port) -> PortDisplay:
        overrides = self.port_displays.get(port)

        port_id: UUID
        if overrides:
            port_id = overrides.id
        else:
            port_id = uuid4_from_hash(f"{self.node_id}|ports|{port.name}")

        return PortDisplay(id=port_id, node_id=self.node_id)

    @classmethod
    def get_from_node_display_registry(cls, node_class: Type[NodeType]) -> Type["BaseNodeDisplay"]:
        return cls._node_display_registry[node_class]

    @cached_property
    def node_id(self) -> UUID:
        """Can be overridden as a class attribute to specify a custom node id."""
        return uuid4_from_hash(self._node.__qualname__)

    @cached_property
    def label(self) -> str:
        """Can be overridden as a class attribute to specify a custom label."""
        return pascal_to_title_case(self._node.__name__)

    @classmethod
    def _get_explicit_node_display_attr(
        cls,
        attribute: str,
        attribute_type: Type[_NodeDisplayAttrType],
    ) -> Optional[_NodeDisplayAttrType]:
        node_display_attribute: Optional[_NodeDisplayAttrType] = getattr(cls, attribute, None)

        if node_display_attribute is None:
            return None

        if isinstance(node_display_attribute, attribute_type):
            return node_display_attribute

        raise ValueError(f"Node {cls.__name__} must define an explicit {attribute} of type {attribute_type.__name__}.")

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        original_base = get_original_base(cls)
        node_class = get_args(original_base)[0]
        if isinstance(node_class, TypeVar):
            bounded_class = node_class.__bound__
            if inspect.isclass(bounded_class) and issubclass(bounded_class, BaseNode):
                cls._node_display_registry[bounded_class] = cls
        elif issubclass(node_class, BaseNode):
            if has_wrapped_node(node_class):
                wrapped_node = get_wrapped_node(node_class)
                if wrapped_node._is_wrapped_node:
                    cls._node_display_registry[wrapped_node] = cls
                    return

            cls._node_display_registry[node_class] = cls
