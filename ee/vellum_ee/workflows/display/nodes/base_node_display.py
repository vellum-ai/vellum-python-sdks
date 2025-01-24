from functools import cached_property
import inspect
from uuid import UUID
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    ForwardRef,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    cast,
    get_args,
    get_origin,
)

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.expressions.between import BetweenExpression
from vellum.workflows.expressions.is_nil import IsNilExpression
from vellum.workflows.expressions.is_not_nil import IsNotNilExpression
from vellum.workflows.expressions.is_not_null import IsNotNullExpression
from vellum.workflows.expressions.is_not_undefined import IsNotUndefinedExpression
from vellum.workflows.expressions.is_null import IsNullExpression
from vellum.workflows.expressions.is_undefined import IsUndefinedExpression
from vellum.workflows.expressions.not_between import NotBetweenExpression
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.references import OutputReference
from vellum.workflows.references.execution_count import ExecutionCountReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.references.workflow_input import WorkflowInputReference
from vellum.workflows.types.core import JsonObject
from vellum.workflows.types.generics import NodeType
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.names import pascal_to_title_case
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay, PortDisplay, PortDisplayOverrides
from vellum_ee.workflows.display.utils.vellum import convert_descriptor_to_operator, primitive_to_vellum_value
from vellum_ee.workflows.display.vellum import CodeResourceDefinition

if TYPE_CHECKING:
    from vellum_ee.workflows.display.types import WorkflowDisplayContext

_NodeDisplayAttrType = TypeVar("_NodeDisplayAttrType")


class BaseNodeDisplayMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        cls = super().__new__(mcs, name, bases, dct)
        if isinstance(dct.get("node_id"), UUID):
            # Display classes are able to override the id of the node class it's parameterized by
            base_node_display_class = cast(Type["BaseNodeDisplay"], cls)
            node_class = base_node_display_class.infer_node_class()
            node_class.__id__ = dct["node_id"]
        return cls


class BaseNodeDisplay(Generic[NodeType], metaclass=BaseNodeDisplayMeta):
    output_display: Dict[OutputReference, NodeOutputDisplay] = {}
    port_displays: Dict[Port, PortDisplayOverrides] = {}

    # Used to store the mapping between node types and their display classes
    _node_display_registry: Dict[Type[NodeType], Type["BaseNodeDisplay"]] = {}

    def serialize(self, display_context: "WorkflowDisplayContext", **kwargs: Any) -> JsonObject:
        raise NotImplementedError(f"Serialization for nodes of type {self._node.__name__} is not supported.")

    def get_base(self) -> CodeResourceDefinition:
        node = self._node

        base_node_classes = [base for base in node.__bases__ if issubclass(base, BaseNode)]
        if len(base_node_classes) != 1:
            raise ValueError(f"Node {node.__name__} must extend from exactly one parent node class.")

        base_node_class = base_node_classes[0]

        return CodeResourceDefinition(
            name=base_node_class.__name__,
            module=base_node_class.__module__.split("."),
        )

    def get_definition(self) -> CodeResourceDefinition:
        node = self._node
        node_definition = CodeResourceDefinition(
            name=node.__name__,
            module=node.__module__.split("."),
        )
        return node_definition

    def get_trigger_id(self) -> UUID:
        return uuid4_from_hash(f"{self.node_id}|trigger")

    def get_node_output_display(self, output: OutputReference) -> Tuple[Type[BaseNode], NodeOutputDisplay]:
        explicit_display = self.output_display.get(output)
        if explicit_display:
            return self._node, explicit_display

        return (self._node, NodeOutputDisplay(id=uuid4_from_hash(f"{self.node_id}|{output.name}"), name=output.name))

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

    @classmethod
    def infer_node_class(cls) -> Type[NodeType]:
        original_base = get_original_base(cls)
        node_class = get_args(original_base)[0]
        if isinstance(node_class, TypeVar):
            bounded_class = node_class.__bound__
            if inspect.isclass(bounded_class) and issubclass(bounded_class, BaseNode):
                return cast(Type[NodeType], bounded_class)

            if isinstance(bounded_class, ForwardRef) and bounded_class.__forward_arg__ == BaseNode.__name__:
                return cast(Type[NodeType], BaseNode)

        if issubclass(node_class, BaseNode):
            return node_class

        raise ValueError(f"Node {cls.__name__} must be a subclass of {BaseNode.__name__}")

    @cached_property
    def node_id(self) -> UUID:
        """Can be overridden as a class attribute to specify a custom node id."""
        return uuid4_from_hash(self._node.__qualname__)

    @cached_property
    def label(self) -> str:
        """Can be overridden as a class attribute to specify a custom label."""
        return pascal_to_title_case(self._node.__name__)

    @property
    def _node(self) -> Type[NodeType]:
        return self.infer_node_class()

    @classmethod
    def _get_explicit_node_display_attr(
        cls,
        attribute: str,
        attribute_type: Type[_NodeDisplayAttrType],
    ) -> Optional[_NodeDisplayAttrType]:
        node_display_attribute: Optional[_NodeDisplayAttrType] = getattr(cls, attribute, None)

        if node_display_attribute is None:
            return None

        origin = get_origin(attribute_type)
        args = get_args(attribute_type)

        if origin is not None:
            # Handle Dict
            if origin is dict and isinstance(node_display_attribute, dict):
                if len(args) == 2:
                    key_type, value_type = args
                    if all(
                        isinstance(k, key_type) and isinstance(v, value_type) for k, v in node_display_attribute.items()
                    ):
                        return cast(_NodeDisplayAttrType, node_display_attribute)
                raise ValueError(f"Node {cls.__name__} must define an explicit {attribute} of type {attribute_type}.")

            # Handle List
            elif origin is list and isinstance(node_display_attribute, list):
                if len(args) == 1:
                    item_type = args[0]
                    if all(isinstance(item, item_type) for item in node_display_attribute):
                        return cast(_NodeDisplayAttrType, node_display_attribute)
                raise ValueError(f"Node {cls.__name__} must define an explicit {attribute} of type {attribute_type}.")

            raise ValueError(f"Node {cls.__name__} must define an explicit {attribute} of type {attribute_type}.")

        if isinstance(node_display_attribute, attribute_type):
            return node_display_attribute

        raise ValueError(f"Node {cls.__name__} must define an explicit {attribute} of type {attribute_type.__name__}.")

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        node_class = cls.infer_node_class()
        cls._node_display_registry[node_class] = cls

    def serialize_condition(self, display_context: "WorkflowDisplayContext", condition: BaseDescriptor) -> JsonObject:
        if isinstance(
            condition,
            (
                IsNullExpression,
                IsNotNullExpression,
                IsNilExpression,
                IsNotNilExpression,
                IsUndefinedExpression,
                IsNotUndefinedExpression,
            ),
        ):
            lhs = self.serialize_value(display_context, condition._expression)
            return {
                "type": "UNARY_EXPRESSION",
                "lhs": lhs,
                "operator": convert_descriptor_to_operator(condition),
            }
        elif isinstance(condition, (BetweenExpression, NotBetweenExpression)):
            base = self.serialize_value(display_context, condition._value)
            lhs = self.serialize_value(display_context, condition._start)
            rhs = self.serialize_value(display_context, condition._end)

            return {
                "type": "TERNARY_EXPRESSION",
                "base": base,
                "operator": convert_descriptor_to_operator(condition),
                "lhs": lhs,
                "rhs": rhs,
            }
        else:
            lhs = self.serialize_value(display_context, condition._lhs)  # type: ignore[attr-defined]
            rhs = self.serialize_value(display_context, condition._rhs)  # type: ignore[attr-defined]

            return {
                "type": "BINARY_EXPRESSION",
                "lhs": lhs,
                "operator": convert_descriptor_to_operator(condition),
                "rhs": rhs,
            }

    def serialize_value(self, display_context: "WorkflowDisplayContext", value: BaseDescriptor) -> JsonObject:
        if isinstance(value, WorkflowInputReference):
            workflow_input_display = display_context.global_workflow_input_displays[value]
            return {
                "type": "WORKFLOW_INPUT",
                "input_variable_id": str(workflow_input_display.id),
            }

        if isinstance(value, OutputReference):
            upstream_node, output_display = display_context.global_node_output_displays[value]
            upstream_node_display = display_context.global_node_displays[upstream_node]

            return {
                "type": "NODE_OUTPUT",
                "node_id": str(upstream_node_display.node_id),
                "node_output_id": str(output_display.id),
            }

        if isinstance(value, VellumSecretReference):
            return {
                "type": "VELLUM_SECRET",
                "vellum_secret_name": value.name,
            }

        if isinstance(value, ExecutionCountReference):
            node_class_display = display_context.global_node_displays[value.node_class]

            return {
                "type": "EXECUTION_COUNTER",
                "node_id": str(node_class_display.node_id),
            }

        if not isinstance(value, BaseDescriptor):
            vellum_value = primitive_to_vellum_value(value)
            return {
                "type": "CONSTANT_VALUE",
                "value": vellum_value.dict(),
            }

        # If it's not any of the references we know about,
        # then try to serialize it as a nested value
        return self.serialize_condition(display_context, value)
