from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import field
from datetime import datetime
import logging
from queue import Queue
from threading import Lock
from uuid import UUID, uuid4
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    SupportsIndex,
    Tuple,
    Type,
    Union,
    cast,
)
from typing_extensions import dataclass_transform

from pydantic import GetCoreSchemaHandler, ValidationInfo, field_serializer, field_validator
from pydantic_core import core_schema

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.utils.uuid import is_valid_uuid
from vellum.workflows.constants import undefined
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.references import ExternalInputReference, OutputReference, StateValueReference
from vellum.workflows.state.delta import AppendStateDelta, SetStateDelta, StateDelta
from vellum.workflows.types.definition import CodeResourceDefinition, serialize_type_encoder_with_id
from vellum.workflows.types.generics import StateType, import_workflow_class, is_workflow_class
from vellum.workflows.types.stack import Stack
from vellum.workflows.types.utils import datetime_now, deepcopy_with_exclusions, get_class_attr_names, infer_types

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow
    from vellum.workflows.nodes.bases import BaseNode

logger = logging.getLogger(__name__)


class _Snapshottable:
    _snapshot_callback: Callable[[Optional[StateDelta]], None]
    _path: str

    def __bind__(self, path: str, snapshot_callback: Callable[[Optional[StateDelta]], None]) -> None:
        self._snapshot_callback = snapshot_callback
        self._path = path


@dataclass_transform(kw_only_default=True)
class _BaseStateMeta(type):
    def __getattribute__(cls, name: str) -> Any:
        if not name.startswith("_"):
            instance = vars(cls).get(name, undefined)
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
        self._snapshot_callback(SetStateDelta(name=f"{self._path}.{key}", delta=value))

    def __deepcopy__(self, memo: Any) -> "_SnapshottableDict":
        y: dict = {}
        memo[id(self)] = y
        for key, value in self.items():
            y[deepcopy(key, memo)] = deepcopy(value, memo)

        y = _SnapshottableDict(y)
        y.__bind__(self._path, self._snapshot_callback)
        memo[id(self)] = y
        return y


class _SnapshottableList(list, _Snapshottable):
    def __setitem__(self, index: Union[SupportsIndex, slice], value: Any) -> None:
        super().__setitem__(index, value)
        if isinstance(index, int):
            self._snapshot_callback(SetStateDelta(name=f"{self._path}.{index}", delta=value))

    def append(self, value: Any) -> None:
        super().append(value)
        self._snapshot_callback(AppendStateDelta(name=self._path, delta=value))

    def __deepcopy__(self, memo: Any) -> "_SnapshottableList":
        y: list = []
        memo[id(self)] = y
        append = y.append
        for a in self:
            append(deepcopy(a, memo))

        y = _SnapshottableList(y)
        y.__bind__(self._path, self._snapshot_callback)
        memo[id(self)] = y
        return y


def _make_snapshottable(path: str, value: Any, snapshot_callback: Callable[[Optional[StateDelta]], None]) -> Any:
    """
    Edits any value to make it snapshottable on edit. Made as a separate function from `BaseState` to
    avoid namespace conflicts with subclasses.
    """
    if isinstance(value, _Snapshottable):
        return value

    if isinstance(value, dict):
        snapshottable_dict = _SnapshottableDict(value)
        snapshottable_dict.__bind__(path, snapshot_callback)
        return snapshottable_dict

    if isinstance(value, list):
        snapshottable_list = _SnapshottableList(value)
        snapshottable_list.__bind__(path, snapshot_callback)
        return snapshottable_list

    return value


NodeExecutionsFulfilled = Dict[Type["BaseNode"], Stack[UUID]]
NodeExecutionsInitiated = Dict[Type["BaseNode"], Set[UUID]]
NodeExecutionsQueued = Dict[Type["BaseNode"], List[UUID]]
NodeExecutionLookup = Dict[UUID, Type["BaseNode"]]
DependenciesInvoked = Dict[UUID, Set[UUID]]


class NodeExecutionCache:
    _node_executions_fulfilled: NodeExecutionsFulfilled
    _node_executions_initiated: NodeExecutionsInitiated
    _node_executions_queued: NodeExecutionsQueued
    _dependencies_invoked: DependenciesInvoked

    # Derived fields - no need to serialize
    __node_execution_lookup__: NodeExecutionLookup  # execution_id -> node_class

    def __init__(self) -> None:
        self._dependencies_invoked = defaultdict(set)
        self._node_executions_fulfilled = defaultdict(Stack[UUID])
        self._node_executions_initiated = defaultdict(set)
        self._node_executions_queued = defaultdict(list)
        self.__node_execution_lookup__ = {}

    @classmethod
    def deserialize(cls, raw_data: dict, nodes: Dict[Union[str, UUID], Type["BaseNode"]]):
        cache = cls()

        def get_node_class(node_id: Any) -> Optional[Type["BaseNode"]]:
            if not isinstance(node_id, str):
                return None

            if is_valid_uuid(node_id):
                return nodes.get(UUID(node_id))

            return nodes.get(node_id)

        dependencies_invoked = raw_data.get("dependencies_invoked")
        if isinstance(dependencies_invoked, dict):
            for execution_id, dependencies in dependencies_invoked.items():
                dependency_execution_ids = {UUID(dep) for dep in dependencies if is_valid_uuid(dep)}
                cache._dependencies_invoked[UUID(execution_id)] = dependency_execution_ids

        node_executions_fulfilled = raw_data.get("node_executions_fulfilled")
        if isinstance(node_executions_fulfilled, dict):
            for node, execution_ids in node_executions_fulfilled.items():
                node_class = get_node_class(node)
                if not node_class:
                    continue

                cache._node_executions_fulfilled[node_class].extend(
                    UUID(execution_id) for execution_id in execution_ids
                )

        node_executions_initiated = raw_data.get("node_executions_initiated")
        if isinstance(node_executions_initiated, dict):
            for node, execution_ids in node_executions_initiated.items():
                node_class = get_node_class(node)
                if not node_class:
                    continue

                cache._node_executions_initiated[node_class].update(
                    {UUID(execution_id) for execution_id in execution_ids}
                )

            for node_class, execution_ids in cache._node_executions_initiated.items():
                for execution_id in execution_ids:
                    cache.__node_execution_lookup__[execution_id] = node_class

        node_executions_queued = raw_data.get("node_executions_queued")
        if isinstance(node_executions_queued, dict):
            for node, execution_ids in node_executions_queued.items():
                node_class = get_node_class(node)
                if not node_class:
                    continue

                cache._node_executions_queued[node_class].extend(UUID(execution_id) for execution_id in execution_ids)

        return cache

    def _invoke_dependency(
        self,
        execution_id: UUID,
        node: Type["BaseNode"],
        invoked_by: UUID,
        dependencies: Set["Type[BaseNode]"],
    ) -> None:
        self._dependencies_invoked[execution_id].add(invoked_by)
        invoked_node_classes = {
            self.__node_execution_lookup__[dep]
            for dep in self._dependencies_invoked[execution_id]
            if dep in self.__node_execution_lookup__
        }
        if len(invoked_node_classes) != len(dependencies):
            return

        if any(dep not in invoked_node_classes for dep in dependencies):
            return

        self._node_executions_queued[node].remove(execution_id)

    def is_node_execution_initiated(self, node: Type["BaseNode"], execution_id: UUID) -> bool:
        return execution_id in self._node_executions_initiated[node]

    def initiate_node_execution(self, node: Type["BaseNode"], execution_id: UUID) -> None:
        self._node_executions_initiated[node].add(execution_id)
        self.__node_execution_lookup__[execution_id] = node

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
                str(node.__id__): list(execution_ids) for node, execution_ids in self._node_executions_initiated.items()
            },
            "node_executions_fulfilled": {
                str(node.__id__): execution_ids.dump()
                for node, execution_ids in self._node_executions_fulfilled.items()
            },
            "node_executions_queued": {
                str(node.__id__): execution_ids for node, execution_ids in self._node_executions_queued.items()
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
    workflow_definition: Type["BaseWorkflow"] = field(default_factory=import_workflow_class)
    id: UUID = field(default_factory=uuid4_default_factory)
    span_id: UUID = field(default_factory=uuid4_default_factory)
    updated_ts: datetime = field(default_factory=default_datetime_factory)
    workflow_inputs: BaseInputs = field(default_factory=BaseInputs)
    external_inputs: Dict[ExternalInputReference, Any] = field(default_factory=dict)
    node_outputs: Dict[OutputReference, Any] = field(default_factory=dict)
    node_execution_cache: NodeExecutionCache = field(default_factory=NodeExecutionCache)
    parent: Optional["BaseState"] = None
    __snapshot_callback__: Optional[Callable[[Optional[StateDelta]], None]] = field(init=False, default=None)

    def model_post_init(self, context: Any) -> None:
        self.__snapshot_callback__ = None

    def add_snapshot_callback(self, callback: Callable[[Optional[StateDelta]], None]) -> None:
        self.node_outputs = _make_snapshottable("meta.node_outputs", self.node_outputs, callback)
        self.external_inputs = _make_snapshottable("meta.external_inputs", self.external_inputs, callback)
        self.__snapshot_callback__ = callback

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("__") or name == "updated_ts":
            super().__setattr__(name, value)
            return

        super().__setattr__(name, value)
        if callable(self.__snapshot_callback__):
            self.__snapshot_callback__(SetStateDelta(name=f"meta.{name}", delta=value))

    @field_serializer("workflow_definition")
    def serialize_workflow_definition(self, workflow_definition: Type["BaseWorkflow"], _info: Any) -> Dict[str, Any]:
        return serialize_type_encoder_with_id(workflow_definition)

    @field_validator("workflow_definition", mode="before")
    @classmethod
    def deserialize_workflow_definition(cls, workflow_definition: Any, info: ValidationInfo):
        if isinstance(workflow_definition, dict):
            deserialized_workflow_definition = CodeResourceDefinition.model_validate(workflow_definition).decode()
            if not is_workflow_class(deserialized_workflow_definition):
                return import_workflow_class()

            return deserialized_workflow_definition

        if is_workflow_class(workflow_definition):
            return workflow_definition

        return import_workflow_class()

    @field_serializer("node_outputs")
    def serialize_node_outputs(self, node_outputs: Dict[OutputReference, Any], _info: Any) -> Dict[str, Any]:
        return {str(descriptor.id): value for descriptor, value in node_outputs.items()}

    @field_validator("node_outputs", mode="before")
    @classmethod
    def deserialize_node_outputs(cls, node_outputs: Any, info: ValidationInfo):
        if isinstance(node_outputs, dict):
            workflow_definition = cls._get_workflow(info)
            if not workflow_definition:
                return node_outputs

            raw_workflow_nodes = workflow_definition.get_nodes()
            workflow_node_outputs: Dict[Union[str, UUID], OutputReference] = {}
            for node in raw_workflow_nodes:
                for output in node.Outputs:
                    workflow_node_outputs[str(output)] = output
                    output_id = node.__output_ids__.get(output.name)
                    if output_id:
                        workflow_node_outputs[output_id] = output

            node_output_keys = list(node_outputs.keys())
            deserialized_node_outputs = {}
            for node_output_key in node_output_keys:
                if is_valid_uuid(node_output_key):
                    output_reference = workflow_node_outputs.get(UUID(node_output_key))
                else:
                    output_reference = workflow_node_outputs.get(node_output_key)

                if not output_reference:
                    continue

                deserialized_node_outputs[output_reference] = node_outputs[node_output_key]

            return deserialized_node_outputs

        return node_outputs

    @field_validator("node_execution_cache", mode="before")
    @classmethod
    def deserialize_node_execution_cache(cls, node_execution_cache: Any, info: ValidationInfo):
        if isinstance(node_execution_cache, dict):
            workflow_definition = cls._get_workflow(info)
            if not workflow_definition:
                return node_execution_cache

            nodes_cache: Dict[Union[str, UUID], Type["BaseNode"]] = {}
            raw_workflow_nodes = workflow_definition.get_nodes()
            for node in raw_workflow_nodes:
                nodes_cache[str(node)] = node
                nodes_cache[node.__id__] = node

            return NodeExecutionCache.deserialize(node_execution_cache, nodes_cache)

        return node_execution_cache

    @field_validator("workflow_inputs", mode="before")
    @classmethod
    def deserialize_workflow_inputs(cls, workflow_inputs: Any, info: ValidationInfo):
        workflow_definition = cls._get_workflow(info)

        if workflow_definition:
            if workflow_inputs is None:
                return workflow_definition.get_inputs_class()()
            if isinstance(workflow_inputs, dict):
                return workflow_definition.get_inputs_class()(**workflow_inputs)

        return workflow_inputs

    @field_serializer("external_inputs")
    def serialize_external_inputs(
        self, external_inputs: Dict[ExternalInputReference, Any], _info: Any
    ) -> Dict[str, Any]:
        return {str(descriptor): value for descriptor, value in external_inputs.items()}

    @field_validator("parent", mode="before")
    @classmethod
    def deserialize_parent(cls, parent: Any, info: ValidationInfo):
        if isinstance(parent, dict):
            workflow_definition = cls._get_workflow(info)
            if not workflow_definition:
                return parent

            parent_meta = parent.get("meta")
            if not isinstance(parent_meta, dict):
                return parent

            parent_workflow_definition = cls.deserialize_workflow_definition(
                parent_meta.get("workflow_definition"), info
            )
            if not is_workflow_class(parent_workflow_definition):
                return parent

            return parent_workflow_definition.deserialize_state(parent)

        return parent

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

    @classmethod
    def _get_workflow(cls, info: ValidationInfo) -> Optional[Type["BaseWorkflow"]]:
        if not info.context:
            return None

        if not isinstance(info.context, dict):
            return None

        workflow_definition = info.context.get("workflow_definition")
        if not is_workflow_class(workflow_definition):
            return None

        return workflow_definition


class BaseState(metaclass=_BaseStateMeta):
    meta: StateMeta = field(init=False)

    __lock__: Lock = field(init=False)
    __is_quiet__: bool = field(init=False)
    __is_atomic__: bool = field(init=False)
    __snapshot_callback__: Callable[["BaseState", List[StateDelta]], None] = field(init=False)
    __deltas__: List[StateDelta] = field(init=False)

    def __init__(self, meta: Optional[StateMeta] = None, **kwargs: Any) -> None:
        self.__is_quiet__ = True
        self.__is_atomic__ = False
        self.__snapshot_callback__ = lambda state, deltas: None
        self.__deltas__ = []
        self.__lock__ = Lock()

        self.meta = meta or StateMeta()
        self.meta.add_snapshot_callback(self.__snapshot__)

        # Make all class attribute values snapshottable
        for name, value in self.__class__.__dict__.items():
            if not name.startswith("_") and name != "meta":
                # Bypass __is_quiet__ instead of `setattr`
                snapshottable_value = _make_snapshottable(name, value, self.__snapshot__)
                super().__setattr__(name, snapshottable_value)

        for name, value in kwargs.items():
            setattr(self, name, value)

        self.__is_quiet__ = False

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

    def __setattr__(self, name: str, delta: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, delta)
            return

        snapshottable_value = _make_snapshottable(name, delta, self.__snapshot__)
        super().__setattr__(name, snapshottable_value)
        self.meta.updated_ts = datetime_now()
        self.__snapshot__(SetStateDelta(name=name, delta=delta))

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

    def __snapshot__(self, delta: Optional[StateDelta] = None) -> None:
        """
        Snapshots the current state to the workflow emitter. The invoked callback is overridden by the
        workflow runner.
        """
        if self.__is_quiet__:
            return

        if delta:
            self.__deltas__.append(delta)

        if self.__is_atomic__:
            return

        try:
            self.__snapshot_callback__(deepcopy(self), self.__deltas__)
        except Exception:
            logger.exception("Failed to snapshot Workflow state.")

        self.__deltas__.clear()

    @contextmanager
    def __quiet__(self):
        prev = self.__is_quiet__
        self.__is_quiet__ = True
        try:
            yield
        finally:
            self.__is_quiet__ = prev

    @contextmanager
    def __atomic__(self):
        prev = self.__is_atomic__
        self.__is_atomic__ = True
        try:
            yield
        finally:
            self.__is_atomic__ = prev
            self.__snapshot__()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
