from collections import defaultdict
from copy import deepcopy
from dataclasses import field
from datetime import datetime
from queue import Queue
from threading import Lock
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Optional, Sequence, Set, Tuple, Type, cast
from typing_extensions import dataclass_transform

from pydantic import GetCoreSchemaHandler, field_serializer
from pydantic_core import core_schema

from vellum.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.constants import undefined
from vellum.workflows.edges.edge import Edge
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.references import ExternalInputReference, OutputReference, StateValueReference
from vellum.workflows.types.generics import StateType
from vellum.workflows.types.stack import Stack
from vellum.workflows.types.utils import (
    datetime_now,
    deepcopy_with_exclusions,
    get_class_attr_names,
    get_class_by_qualname,
    infer_types,
)

if TYPE_CHECKING:
    from vellum.workflows.nodes.bases import BaseNode


class _Snapshottable:
    _snapshot_callback: Callable[[], None]

    def __deepcopy__(self, memo: Any) -> "_Snapshottable":
        return deepcopy_with_exclusions(
            self,
            memo=memo,
            exclusions={
                "_snapshot_callback": self._snapshot_callback,
            },
        )


@dataclass_transform(kw_only_default=True)
class _BaseStateMeta(type):
    def __getattribute__(cls, name: str) -> Any:
        if not name.startswith("_"):
            instance = vars(cls).get(name)
            types = infer_types(cls, name)
            return StateValueReference(name=name, types=types, instance=instance)

        return super().__getattribute__(name)

    def __iter__(cls) -> Iterator[StateValueReference]:
        # We iterate through the inheritance hierarchy to find all the StateValueReference attached to this
        # Inputs class. __mro__ is the method resolution order, which is the order in which base classes are resolved.
        for resolved_cls in cls.__mro__:
            attr_names = get_class_attr_names(resolved_cls)
            for attr_name in attr_names:
                if attr_name == "meta":
                    continue
                attr_value = getattr(resolved_cls, attr_name)
                if not isinstance(attr_value, (StateValueReference)):
                    continue

                yield attr_value


class _SnapshottableDict(dict, _Snapshottable):
    def __setitem__(self, key: Any, value: Any) -> None:
        super().__setitem__(key, value)
        self._snapshot_callback()


def _make_snapshottable(value: Any, snapshot_callback: Callable[[], None]) -> Any:
    """
    Edits any value to make it snapshottable on edit. Made as a separate function from `BaseState` to
    avoid namespace conflicts with subclasses.
    """
    if isinstance(value, _Snapshottable):
        return value

    if isinstance(value, dict):
        snapshottable_dict = _SnapshottableDict(value)
        snapshottable_dict._snapshot_callback = snapshot_callback
        return snapshottable_dict

    return value


class NodeExecutionCache:
    _node_executions_fulfilled: Dict[Type["BaseNode"], Stack[UUID]]
    _node_executions_initiated: Dict[Type["BaseNode"], Set[UUID]]
    _node_executions_queued: Dict[Type["BaseNode"], List[UUID]]
    _dependencies_invoked: Dict[UUID, Set[Type["BaseNode"]]]

    def __init__(
        self,
        dependencies_invoked: Optional[Dict[str, Sequence[str]]] = None,
        node_executions_fulfilled: Optional[Dict[str, Sequence[str]]] = None,
        node_executions_initiated: Optional[Dict[str, Sequence[str]]] = None,
        node_executions_queued: Optional[Dict[str, Sequence[str]]] = None,
    ) -> None:
        self._dependencies_invoked = defaultdict(set)
        self._node_executions_fulfilled = defaultdict(Stack[UUID])
        self._node_executions_initiated = defaultdict(set)
        self._node_executions_queued = defaultdict(list)

        for execution_id, dependencies in (dependencies_invoked or {}).items():
            self._dependencies_invoked[UUID(execution_id)] = {get_class_by_qualname(dep) for dep in dependencies}

        for node, execution_ids in (node_executions_fulfilled or {}).items():
            node_class = get_class_by_qualname(node)
            self._node_executions_fulfilled[node_class].extend(UUID(execution_id) for execution_id in execution_ids)

        for node, execution_ids in (node_executions_initiated or {}).items():
            node_class = get_class_by_qualname(node)
            self._node_executions_initiated[node_class].update({UUID(execution_id) for execution_id in execution_ids})

        for node, execution_ids in (node_executions_queued or {}).items():
            node_class = get_class_by_qualname(node)
            self._node_executions_queued[node_class].extend(UUID(execution_id) for execution_id in execution_ids)

    def _invoke_dependency(
        self,
        execution_id: UUID,
        node: Type["BaseNode"],
        dependency: Type["BaseNode"],
        dependencies: Set["Type[BaseNode]"],
    ) -> None:
        self._dependencies_invoked[execution_id].add(dependency)
        if all(dep in self._dependencies_invoked[execution_id] for dep in dependencies):
            self._node_executions_queued[node].remove(execution_id)

    def queue_node_execution(
        self, node: Type["BaseNode"], dependencies: Set["Type[BaseNode]"], invoked_by: Optional[Edge] = None
    ) -> UUID:
        execution_id = uuid4()
        if not invoked_by:
            return execution_id

        source_node = invoked_by.from_port.node_class
        for queued_node_execution_id in self._node_executions_queued[node]:
            if source_node not in self._dependencies_invoked[queued_node_execution_id]:
                self._invoke_dependency(queued_node_execution_id, node, source_node, dependencies)
                return queued_node_execution_id

        self._node_executions_queued[node].append(execution_id)
        self._invoke_dependency(execution_id, node, source_node, dependencies)
        return execution_id

    def is_node_execution_initiated(self, node: Type["BaseNode"], execution_id: UUID) -> bool:
        return execution_id in self._node_executions_initiated[node]

    def initiate_node_execution(self, node: Type["BaseNode"], execution_id: UUID) -> None:
        self._node_executions_initiated[node].add(execution_id)

    def fulfill_node_execution(self, node: Type["BaseNode"], execution_id: UUID) -> None:
        self._node_executions_fulfilled[node].push(execution_id)

    def get_execution_count(self, node: Type["BaseNode"]) -> int:
        return self._node_executions_fulfilled[node].size()

    def dump(self) -> Dict[str, Any]:
        return {
            "dependencies_invoked": {
                str(execution_id): [str(dep) for dep in dependencies]
                for execution_id, dependencies in self._dependencies_invoked.items()
            },
            "node_executions_initiated": {
                str(node): list(execution_ids) for node, execution_ids in self._node_executions_initiated.items()
            },
            "node_executions_fulfilled": {
                str(node): execution_ids.dump() for node, execution_ids in self._node_executions_fulfilled.items()
            },
            "node_executions_queued": {
                str(node): execution_ids for node, execution_ids in self._node_executions_queued.items()
            },
        }

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)


def uuid4_default_factory() -> UUID:
    """
    Allows us to mock the uuid4 for testing.
    """
    return uuid4()


def default_datetime_factory() -> datetime:
    """
    Makes it possible to mock the datetime factory for testing.
    """

    return datetime_now()


class StateMeta(UniversalBaseModel):
    id: UUID = field(default_factory=uuid4_default_factory)
    trace_id: UUID = field(default_factory=uuid4_default_factory)
    span_id: UUID = field(default_factory=uuid4_default_factory)
    updated_ts: datetime = field(default_factory=default_datetime_factory)
    workflow_inputs: BaseInputs = field(default_factory=BaseInputs)
    external_inputs: Dict[ExternalInputReference, Any] = field(default_factory=dict)
    node_outputs: Dict[OutputReference, Any] = field(default_factory=dict)
    node_execution_cache: NodeExecutionCache = field(default_factory=NodeExecutionCache)
    parent: Optional["BaseState"] = None
    __snapshot_callback__: Optional[Callable[[], None]] = field(init=False, default=None)

    def model_post_init(self, context: Any) -> None:
        if self.parent:
            self.trace_id = self.parent.meta.trace_id
        self.__snapshot_callback__ = None

    def add_snapshot_callback(self, callback: Callable[[], None]) -> None:
        self.node_outputs = _make_snapshottable(self.node_outputs, callback)
        self.external_inputs = _make_snapshottable(self.external_inputs, callback)
        self.__snapshot_callback__ = callback

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("__") or name == "updated_ts":
            super().__setattr__(name, value)
            return

        super().__setattr__(name, value)
        if callable(self.__snapshot_callback__):
            self.__snapshot_callback__()

    @field_serializer("node_outputs")
    def serialize_node_outputs(self, node_outputs: Dict[OutputReference, Any], _info: Any) -> Dict[str, Any]:
        return {str(descriptor): value for descriptor, value in node_outputs.items()}

    @field_serializer("external_inputs")
    def serialize_external_inputs(
        self, external_inputs: Dict[ExternalInputReference, Any], _info: Any
    ) -> Dict[str, Any]:
        return {str(descriptor): value for descriptor, value in external_inputs.items()}

    def __deepcopy__(self, memo: Optional[Dict[int, Any]] = None) -> "StateMeta":
        if not memo:
            memo = {}

        new_node_outputs = {
            descriptor: value if isinstance(value, Queue) else deepcopy(value, memo)
            for descriptor, value in self.node_outputs.items()
        }

        new_external_inputs = {
            descriptor: value if isinstance(value, Queue) else deepcopy(value, memo)
            for descriptor, value in self.external_inputs.items()
        }

        memo[id(self.node_outputs)] = new_node_outputs
        memo[id(self.external_inputs)] = new_external_inputs
        memo[id(self.__snapshot_callback__)] = None

        return super().__deepcopy__(memo)


class BaseState(metaclass=_BaseStateMeta):
    meta: StateMeta = field(init=False)

    __lock__: Lock = field(init=False)
    __is_initializing__: bool = field(init=False)
    __snapshot_callback__: Callable[["BaseState"], None] = field(init=False)

    def __init__(self, meta: Optional[StateMeta] = None, **kwargs: Any) -> None:
        self.__is_initializing__ = True
        self.__snapshot_callback__ = lambda state: None
        self.__lock__ = Lock()

        self.meta = meta or StateMeta()
        self.meta.add_snapshot_callback(self.__snapshot__)

        # Make all class attribute values snapshottable
        for name, value in self.__class__.__dict__.items():
            if not name.startswith("_") and name != "meta":
                # Bypass __is_initializing__ instead of `setattr`
                snapshottable_value = _make_snapshottable(value, self.__snapshot__)
                super().__setattr__(name, snapshottable_value)

        for name, value in kwargs.items():
            setattr(self, name, value)

        self.__is_initializing__ = False

    def __deepcopy__(self, memo: Any) -> "BaseState":
        new_state = deepcopy_with_exclusions(
            self,
            exclusions={
                "__lock__": Lock(),
            },
            memo=memo,
        )
        new_state.meta.add_snapshot_callback(new_state.__snapshot__)
        return new_state

    def __repr__(self) -> str:
        values = "\n".join(
            [f"    {key}={value}" for key, value in vars(self).items() if not key.startswith("_") and key != "meta"]
        )
        node_outputs = "\n".join([f"            {key}={value}" for key, value in self.meta.node_outputs.items()])
        return f"""\
{self.__class__.__name__}:
{values}
    meta:
        id={self.meta.id}
        updated_ts={self.meta.updated_ts}
        node_outputs:{' Empty' if not node_outputs else ''}
{node_outputs}
"""

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        """
        Returns an iterator treating all state keys as (key, value) items, allowing consumers to call `dict()`
        on an instance of this class.
        """

        # If the user sets a default value on state (e.g. something = "foo"), it's not on `instance_attributes` below.
        # So we need to include class_attributes here just in case
        class_attributes = {key: value for key, value in self.__class__.__dict__.items() if not key.startswith("_")}
        instance_attributes = {key: value for key, value in self.__dict__.items() if not key.startswith("__")}

        all_attributes = {**class_attributes, **instance_attributes}
        items = [(key, value) for key, value in all_attributes.items() if key not in ["_lock"]]
        return iter(items)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_") or self.__is_initializing__:
            super().__setattr__(name, value)
            return

        snapshottable_value = _make_snapshottable(value, self.__snapshot__)
        super().__setattr__(name, snapshottable_value)
        self.meta.updated_ts = datetime_now()
        self.__snapshot__()

    def __add__(self, other: StateType) -> StateType:
        """
        Handles merging two states together, preferring the latest state by updated_ts for any given node output.
        """

        if not isinstance(other, type(self)):
            raise TypeError(f"Cannot add {type(other).__name__} to {type(self).__name__}]")

        latest_state = self if self.meta.updated_ts >= other.meta.updated_ts else other
        oldest_state = other if latest_state == self else self

        for descriptor, value in oldest_state.meta.node_outputs.items():
            if descriptor not in latest_state.meta.node_outputs:
                latest_state.meta.node_outputs[descriptor] = value

        for key, value in oldest_state:
            if not isinstance(key, str):
                continue

            if key.startswith("_"):
                continue

            if getattr(latest_state, key, undefined) == undefined:
                setattr(latest_state, key, value)

        return cast(StateType, latest_state)

    def __snapshot__(self) -> None:
        """
        Snapshots the current state to the workflow emitter. The invoked callback is overridden by the
        workflow runner.
        """
        self.__snapshot_callback__(deepcopy(self))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
