from dataclasses import field
from functools import cached_property, reduce
import inspect
from types import MappingProxyType
from uuid import UUID
from typing import Any, Dict, Generic, Iterator, Optional, Set, Tuple, Type, TypeVar, Union, cast, get_args

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import is_unresolved, resolve_value
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.graph import Graph
from vellum.workflows.graph.graph import GraphTarget
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.outputs import BaseOutput, BaseOutputs
from vellum.workflows.ports.node_ports import NodePorts
from vellum.workflows.ports.port import Port
from vellum.workflows.references import ExternalInputReference
from vellum.workflows.references.execution_count import ExecutionCountReference
from vellum.workflows.references.node import NodeReference
from vellum.workflows.references.output import OutputReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.core import MergeBehavior
from vellum.workflows.types.generics import StateType
from vellum.workflows.types.utils import get_class_attr_names, get_original_base, infer_types
from vellum.workflows.utils.uuids import uuid4_from_hash


def is_nested_class(nested: Any, parent: Type) -> bool:
    return (
        inspect.isclass(nested)
        # If a class is defined within a function, we don't consider it nested in the class defining that function
        # The example of this is a Subworkflow defined within TryNode.wrap()
        and (len(nested.__qualname__.split(".")) < 2 or nested.__qualname__.split(".")[-2] != "<locals>")
        and nested.__module__ == parent.__module__
        and (nested.__qualname__.startswith(parent.__name__) or nested.__qualname__.startswith(parent.__qualname__))
    ) or any(is_nested_class(nested, base) for base in parent.__bases__)


class BaseNodeMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        # TODO: Inherit the inner Output classes from every base class.
        #   https://app.shortcut.com/vellum/story/4007/support-auto-inheriting-parent-node-outputs

        if "Outputs" in dct:
            outputs_class = dct["Outputs"]
            if not any(issubclass(base, BaseOutputs) for base in outputs_class.__bases__):
                parent_outputs_class = next(
                    (base.Outputs for base in bases if hasattr(base, "Outputs")),
                    BaseOutputs,  # Default to BaseOutputs only if no parent has Outputs
                )

                # Filter out object from bases while preserving other inheritance
                filtered_bases = tuple(base for base in outputs_class.__bases__ if base is not object)

                dct["Outputs"] = type(
                    f"{name}.Outputs",
                    (parent_outputs_class,) + filtered_bases,
                    {**outputs_class.__dict__, "__module__": dct["__module__"]},
                )
        else:
            for base in reversed(bases):
                if hasattr(base, "Outputs"):
                    dct["Outputs"] = type(
                        f"{name}.Outputs",
                        (base.Outputs,),
                        {"__module__": dct["__module__"]},
                    )
                    break
            else:
                raise ValueError("Outputs class not found in base classes")

        if "Ports" in dct:
            dct["Ports"] = type(
                f"{name}.Ports",
                (NodePorts,),
                {**dct["Ports"].__dict__, "__module__": dct["__module__"]},
            )
        else:
            for base in reversed(bases):
                if issubclass(base, BaseNode):
                    ports_dct = {p.name: Port(default=p.default) for p in base.Ports}
                    ports_dct["__module__"] = dct["__module__"]
                    dct["Ports"] = type(f"{name}.Ports", (NodePorts,), ports_dct)
                    break

        if "Execution" not in dct:
            for base in reversed(bases):
                if issubclass(base, BaseNode):
                    dct["Execution"] = type(
                        f"{name}.Execution",
                        (base.Execution,),
                        {"__module__": dct["__module__"]},
                    )
                    break

        if "Trigger" not in dct:
            for base in reversed(bases):
                if issubclass(base, BaseNode):
                    trigger_dct = {
                        **base.Trigger.__dict__,
                        "__module__": dct["__module__"],
                    }
                    dct["Trigger"] = type(f"{name}.Trigger", (base.Trigger,), trigger_dct)
                    break

        cls = super().__new__(mcs, name, bases, dct)
        node_class = cast(Type["BaseNode"], cls)

        node_class.Outputs._node_class = node_class

        # Add cls to relevant nested classes, since python should've been doing this by default
        for port in node_class.Ports:
            port.node_class = node_class

        node_class.Execution.node_class = node_class
        node_class.Trigger.node_class = node_class
        node_class.ExternalInputs.__parent_class__ = node_class
        node_class.__id__ = uuid4_from_hash(node_class.__qualname__)
        node_class.__output_ids__ = {
            ref.name: uuid4_from_hash(f"{node_class.__id__}|{ref.name}")
            for ref in node_class.Outputs
            if isinstance(ref, OutputReference)
        }
        return node_class

    @property
    def _localns(cls) -> Dict[str, Any]:
        from vellum.workflows.workflows.base import BaseWorkflow

        return {"BaseWorkflow": BaseWorkflow}

    def __getattribute__(cls, name: str) -> Any:
        attribute = super().__getattribute__(name)
        if (
            name.startswith("_")
            or inspect.isfunction(attribute)
            or inspect.ismethod(attribute)
            or is_nested_class(attribute, cls)
            or isinstance(attribute, (property, cached_property))
            or not issubclass(cls, BaseNode)
        ):
            return attribute

        types = infer_types(cls, name, cls._localns)
        return NodeReference(
            name=name,
            types=types,
            instance=attribute,
            node_class=cls,
        )

    def __rshift__(cls, other_cls: GraphTarget) -> Graph:
        if not issubclass(cls, BaseNode):
            raise ValueError("BaseNodeMeta can only be extended from subclasses of BaseNode")

        if not cls.Ports._default_port:
            raise ValueError("No default port found on node")

        if isinstance(other_cls, Graph) or isinstance(other_cls, set):
            return Graph.from_node(cls) >> other_cls

        return cls.Ports._default_port >> other_cls

    def __rrshift__(cls, other_cls: GraphTarget) -> Graph:
        if not issubclass(cls, BaseNode):
            raise ValueError("BaseNodeMeta can only be extended from subclasses of BaseNode")

        if not isinstance(other_cls, set):
            other_cls = {other_cls}

        return Graph.from_set(other_cls) >> cls

    def __repr__(self) -> str:
        return f"{self.__module__}.{self.__qualname__}"

    def __iter__(cls) -> Iterator[NodeReference]:
        # We iterate through the inheritance hierarchy to find all the OutputDescriptors attached to this Outputs class.
        # __mro__ is the method resolution order, which is the order in which base classes are resolved.
        yielded_attr_names: Set[str] = {"state"}

        for resolved_cls in cls.__mro__:
            attr_names = get_class_attr_names(resolved_cls)
            for attr_name in attr_names:
                if attr_name in yielded_attr_names:
                    continue

                attr_value = getattr(resolved_cls, attr_name, undefined)
                if not isinstance(attr_value, NodeReference):
                    continue

                yield attr_value
                yielded_attr_names.add(attr_name)


class _BaseNodeTriggerMeta(type):
    def __eq__(self, other: Any) -> bool:
        """
        We need to include custom eq logic to prevent infinite loops during ipython reloading.
        """

        if not isinstance(other, _BaseNodeTriggerMeta):
            return False

        if not self.__name__.endswith(".Trigger") or not other.__name__.endswith(".Trigger"):
            return super().__eq__(other)

        self_trigger_class = cast(Type["BaseNode.Trigger"], self)
        other_trigger_class = cast(Type["BaseNode.Trigger"], other)

        return self_trigger_class.node_class.__name__ == other_trigger_class.node_class.__name__


class _BaseNodeExecutionMeta(type):
    def __getattribute__(cls, name: str) -> Any:
        if name == "count" and issubclass(cls, BaseNode.Execution):
            return ExecutionCountReference(cls.node_class)

        return super().__getattribute__(name)

    def __eq__(self, other: Any) -> bool:
        """
        We need to include custom eq logic to prevent infinite loops during ipython reloading.
        """

        if not isinstance(other, _BaseNodeExecutionMeta):
            return False

        if not self.__name__.endswith(".Execution") or not other.__name__.endswith(".Execution"):
            return super().__eq__(other)

        self_execution_class = cast(Type["BaseNode.Execution"], self)
        other_execution_class = cast(Type["BaseNode.Execution"], other)

        return self_execution_class.node_class.__name__ == other_execution_class.node_class.__name__


NodeRunResponse = Union[BaseOutputs, Iterator[BaseOutput]]


class BaseNode(Generic[StateType], metaclass=BaseNodeMeta):
    __id__: UUID = uuid4_from_hash(__qualname__)
    __output_ids__: Dict[str, UUID] = {}
    state: StateType
    _context: WorkflowContext
    _inputs: MappingProxyType[NodeReference, Any]

    class ExternalInputs(BaseInputs):
        __descriptor_class__ = ExternalInputReference

    # TODO: Consider using metaclasses to prevent the need for users to specify that the
    #   "Outputs" class inherits from "BaseOutputs" and do so automatically.
    #   https://app.shortcut.com/vellum/story/4008/auto-inherit-basenodeoutputs-in-outputs-classes
    class Outputs(BaseOutputs):
        _node_class: Type["BaseNode"] = field(init=False)

    class Ports(NodePorts):
        default = Port(default=True)

    class Trigger(metaclass=_BaseNodeTriggerMeta):
        node_class: Type["BaseNode"]
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES

        @classmethod
        def should_initiate(
            cls,
            state: StateType,
            dependencies: Set["Type[BaseNode]"],
            node_span_id: UUID,
        ) -> bool:
            """
            Determines whether a Node's execution should be initiated. Override this method to define custom
            trigger criteria.
            """
            if state.meta.node_execution_cache.is_node_execution_initiated(cls.node_class, node_span_id):
                return False

            if cls.merge_behavior == MergeBehavior.AWAIT_ATTRIBUTES:
                for descriptor in cls.node_class:
                    if not descriptor.instance:
                        continue

                    resolved_value = resolve_value(descriptor.instance, state, path=descriptor.name)
                    if is_unresolved(resolved_value):
                        return False

                return True

            if cls.merge_behavior == MergeBehavior.AWAIT_ANY:
                return True

            if cls.merge_behavior == MergeBehavior.AWAIT_ALL:
                """
                A node utilizing an AWAIT_ALL merge strategy will only be considered ready
                when all of its dependencies have invoked this node.
                """
                # Check if all dependencies have invoked this node
                dependencies_invoked = state.meta.node_execution_cache._dependencies_invoked.get(node_span_id, set())
                all_deps_invoked = all(dep in dependencies_invoked for dep in dependencies)

                return all_deps_invoked

            raise NodeException(
                message="Invalid Trigger Node Specification",
                code=WorkflowErrorCode.INVALID_INPUTS,
            )

    class Execution(metaclass=_BaseNodeExecutionMeta):
        node_class: Type["BaseNode"]
        count: int

    def __init__(
        self,
        *,
        state: Optional[StateType] = None,
        context: Optional[WorkflowContext] = None,
    ):
        if state:
            self.state = state
        else:
            # Instantiate a default state class if one is not provided, for ease of testing

            original_base = get_original_base(self.__class__)

            args = get_args(original_base)

            if args and len(args) > 0:
                state_type = args[0]
                if isinstance(state_type, TypeVar):
                    state_type = BaseState
            else:
                state_type = BaseState

            self.state = state_type()

        self._context = context or WorkflowContext()
        inputs: Dict[str, Any] = {}
        for descriptor in self.__class__:
            if not descriptor.instance:
                continue

            if any(isinstance(t, type) and issubclass(t, BaseDescriptor) for t in descriptor.types):
                # We don't want to resolve attributes that are _meant_ to be descriptors
                continue

            resolved_value = resolve_value(descriptor.instance, self.state, path=descriptor.name, memo=inputs)
            setattr(self, descriptor.name, resolved_value)

        # Resolve descriptors set as defaults to the outputs class
        def _outputs_post_init(outputs_self: "BaseNode.Outputs", **kwargs: Any) -> None:
            for node_output_descriptor in self.Outputs:
                if node_output_descriptor.name in kwargs:
                    continue

                if isinstance(node_output_descriptor.instance, BaseDescriptor):
                    setattr(
                        outputs_self,
                        node_output_descriptor.name,
                        node_output_descriptor.instance.resolve(self.state),
                    )
            delattr(self.Outputs, "_outputs_post_init")

        setattr(self.Outputs, "_outputs_post_init", _outputs_post_init)

        # We only want to store the attributes that were actually set as inputs, not every attribute that exists.
        all_inputs = {}
        for key, value in inputs.items():
            path_parts = key.split(".")
            node_attribute_descriptor = getattr(self.__class__, path_parts[0])
            inputs_key = reduce(lambda acc, part: acc[part], path_parts[1:], node_attribute_descriptor)
            all_inputs[inputs_key] = value

        self._inputs = MappingProxyType(all_inputs)

    def run(self) -> NodeRunResponse:
        return self.Outputs()

    def __repr__(self) -> str:
        return str(self.__class__)
