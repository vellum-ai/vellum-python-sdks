# flake8: noqa: E402

import importlib
import inspect

from vellum.plugins.utils import load_runtime_plugins

load_runtime_plugins()

from datetime import datetime
from functools import lru_cache
from threading import Event as ThreadingEvent
from uuid import uuid4
from typing import (
    Any,
    ClassVar,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
)

from vellum.workflows.edges import Edge
from vellum.workflows.emitters.base import BaseWorkflowEmitter
from vellum.workflows.errors import VellumError, VellumErrorCode
from vellum.workflows.events.node import (
    NodeExecutionFulfilledBody,
    NodeExecutionFulfilledEvent,
    NodeExecutionInitiatedBody,
    NodeExecutionInitiatedEvent,
    NodeExecutionPausedBody,
    NodeExecutionPausedEvent,
    NodeExecutionRejectedBody,
    NodeExecutionRejectedEvent,
    NodeExecutionResumedBody,
    NodeExecutionResumedEvent,
    NodeExecutionStreamingBody,
    NodeExecutionStreamingEvent,
)
from vellum.workflows.events.types import WorkflowEventType
from vellum.workflows.events.workflow import (
    GenericWorkflowEvent,
    WorkflowExecutionFulfilledBody,
    WorkflowExecutionFulfilledEvent,
    WorkflowExecutionInitiatedBody,
    WorkflowExecutionInitiatedEvent,
    WorkflowExecutionPausedBody,
    WorkflowExecutionPausedEvent,
    WorkflowExecutionRejectedBody,
    WorkflowExecutionRejectedEvent,
    WorkflowExecutionResumedBody,
    WorkflowExecutionResumedEvent,
    WorkflowExecutionStreamingBody,
    WorkflowExecutionStreamingEvent,
)
from vellum.workflows.graph import Graph
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.runner import WorkflowRunner
from vellum.workflows.runner.runner import ExternalInputsArg, RunFromNodeArg
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.state.store import Store
from vellum.workflows.types.generics import StateType, WorkflowInputsType
from vellum.workflows.types.utils import get_original_base


class _BaseWorkflowMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        if "graph" not in dct:
            dct["graph"] = []

        return super().__new__(mcs, name, bases, dct)


class BaseWorkflow(Generic[WorkflowInputsType, StateType], metaclass=_BaseWorkflowMeta):
    graph: ClassVar[Union[Type[BaseNode], Graph, Set[Type[BaseNode]], Set[Graph]]]
    emitters: List[BaseWorkflowEmitter]
    resolvers: List[BaseWorkflowResolver]

    class Outputs(BaseOutputs):
        pass

    WorkflowEvent = Union[  # type: ignore
        GenericWorkflowEvent,
        WorkflowExecutionInitiatedEvent[WorkflowInputsType],  # type: ignore[valid-type]
        WorkflowExecutionFulfilledEvent[Outputs],
    ]

    TerminalWorkflowEvent = Union[
        WorkflowExecutionFulfilledEvent[Outputs],
        WorkflowExecutionRejectedEvent,
        WorkflowExecutionPausedEvent,
    ]

    WorkflowEventStream = Generator[WorkflowEvent, None, None]

    def __init__(
        self,
        parent_state: Optional[BaseState] = None,
        emitters: Optional[List[BaseWorkflowEmitter]] = None,
        resolvers: Optional[List[BaseWorkflowResolver]] = None,
        context: Optional[WorkflowContext] = None,
    ):
        self._parent_state = parent_state
        self.emitters = emitters or (self.emitters if hasattr(self, "emitters") else [])
        self.resolvers = resolvers or (self.resolvers if hasattr(self, "resolvers") else [])
        self._context = context or WorkflowContext()
        self._store = Store()

        self.validate()

    @property
    def context(self) -> WorkflowContext:
        return self._context

    @classmethod
    def get_subgraphs(cls) -> List[Graph]:
        original_graph = cls.graph
        if isinstance(original_graph, Graph):
            return [original_graph]
        if isinstance(original_graph, set):
            return [
                subgraph if isinstance(subgraph, Graph) else Graph.from_node(subgraph) for subgraph in original_graph
            ]
        if issubclass(original_graph, BaseNode):
            return [Graph.from_node(original_graph)]

        raise ValueError(f"Unexpected graph type: {original_graph.__class__}")

    @classmethod
    def get_edges(cls) -> Iterator[Edge]:
        """
        Returns an iterator over the edges in the workflow. We use a set to
        ensure uniqueness, and the iterator to preserve order.
        """

        edges = set()
        subgraphs = cls.get_subgraphs()
        for subgraph in subgraphs:
            for edge in subgraph.edges:
                if edge not in edges:
                    edges.add(edge)
                    yield edge

    @classmethod
    def get_nodes(cls) -> Iterator[Type[BaseNode]]:
        """
        Returns an iterator over the nodes in the workflow. We use a set to
        ensure uniqueness, and the iterator to preserve order.
        """

        nodes = set()
        for subgraph in cls.get_subgraphs():
            for node in subgraph.nodes:
                if node not in nodes:
                    nodes.add(node)
                    yield node

    @classmethod
    def get_entrypoints(cls) -> Iterable[Type[BaseNode]]:
        return iter({e for g in cls.get_subgraphs() for e in g.entrypoints})

    def run(
        self,
        inputs: Optional[WorkflowInputsType] = None,
        state: Optional[StateType] = None,
        entrypoint_nodes: Optional[RunFromNodeArg] = None,
        external_inputs: Optional[ExternalInputsArg] = None,
        cancel_signal: Optional[ThreadingEvent] = None,
    ) -> TerminalWorkflowEvent:
        events = WorkflowRunner(
            self,
            inputs=inputs,
            state=state,
            entrypoint_nodes=entrypoint_nodes,
            external_inputs=external_inputs,
            cancel_signal=cancel_signal,
        ).stream()
        first_event: Optional[Union[WorkflowExecutionInitiatedEvent, WorkflowExecutionResumedEvent]] = None
        last_event = None
        for event in events:
            if event.name == "workflow.execution.initiated" or event.name == "workflow.execution.resumed":
                first_event = event
            last_event = event

        if not last_event:
            return WorkflowExecutionRejectedEvent(
                trace_id=uuid4(),
                span_id=uuid4(),
                body=WorkflowExecutionRejectedBody(
                    error=VellumError(code=VellumErrorCode.INTERNAL_ERROR, message="No events were emitted"),
                    workflow_definition=self.__class__,
                ),
            )

        if not first_event:
            return WorkflowExecutionRejectedEvent(
                trace_id=uuid4(),
                span_id=uuid4(),
                body=WorkflowExecutionRejectedBody(
                    error=VellumError(
                        code=VellumErrorCode.INTERNAL_ERROR, message="Initiated event was never emitted"
                    ),
                    workflow_definition=self.__class__,
                ),
            )

        if (
            last_event.name == "workflow.execution.rejected"
            or last_event.name == "workflow.execution.fulfilled"
            or last_event.name == "workflow.execution.paused"
        ):
            return last_event

        return WorkflowExecutionRejectedEvent(
            trace_id=first_event.trace_id,
            span_id=first_event.span_id,
            body=WorkflowExecutionRejectedBody(
                workflow_definition=self.__class__,
                error=VellumError(
                    code=VellumErrorCode.INTERNAL_ERROR,
                    message=f"Unexpected last event name found: {last_event.name}",
                ),
            ),
        )

    def stream(
        self,
        event_types: Optional[Set[WorkflowEventType]] = None,
        inputs: Optional[WorkflowInputsType] = None,
        state: Optional[StateType] = None,
        entrypoint_nodes: Optional[RunFromNodeArg] = None,
        external_inputs: Optional[ExternalInputsArg] = None,
        cancel_signal: Optional[ThreadingEvent] = None,
    ) -> WorkflowEventStream:
        event_types = event_types or {WorkflowEventType.WORKFLOW}
        for event in WorkflowRunner(
            self,
            inputs=inputs,
            state=state,
            entrypoint_nodes=entrypoint_nodes,
            external_inputs=external_inputs,
            cancel_signal=cancel_signal,
        ).stream():
            if WorkflowEventType(event.name.split(".")[0].upper()) in event_types:
                yield event

    def validate(self) -> None:
        """
        Validates the Workflow, by running through our list of linter rules.
        """
        # TODO: Implement rule that all entrypoints are non empty
        # https://app.shortcut.com/vellum/story/4327
        pass

    @classmethod
    @lru_cache
    def _get_parameterized_classes(cls) -> Tuple[Type[WorkflowInputsType], Type[StateType]]:
        original_base = get_original_base(cls)

        inputs_type, state_type = get_args(original_base)

        if isinstance(inputs_type, TypeVar):
            inputs_type = BaseInputs
        if isinstance(state_type, TypeVar):
            state_type = BaseState

        if not issubclass(inputs_type, BaseInputs):
            raise ValueError(f"Expected first type to be a subclass of BaseInputs, was: {inputs_type}")

        if not issubclass(state_type, BaseState):
            raise ValueError(f"Expected second type to be a subclass of BaseState, was: {state_type}")

        return (inputs_type, state_type)

    @classmethod
    def get_inputs_class(cls) -> Type[WorkflowInputsType]:
        return cls._get_parameterized_classes()[0]

    @classmethod
    def get_state_class(cls) -> Type[StateType]:
        return cls._get_parameterized_classes()[1]

    def get_default_inputs(self) -> WorkflowInputsType:
        return self.get_inputs_class()()

    def get_default_state(self, workflow_inputs: Optional[WorkflowInputsType] = None) -> StateType:
        return self.get_state_class()(
            meta=StateMeta(parent=self._parent_state, workflow_inputs=workflow_inputs or self.get_default_inputs())
        )

    def get_state_at_node(self, node: Type[BaseNode]) -> StateType:
        event_ts = datetime.min
        for event in self._store.events:
            if event.name == "node.execution.initiated" and event.node_definition == node:
                event_ts = event.timestamp

        most_recent_state_snapshot: Optional[StateType] = None
        for snapshot in self._store.state_snapshots:
            if snapshot.meta.updated_ts > event_ts:
                break

            most_recent_state_snapshot = cast(StateType, snapshot)

        if not most_recent_state_snapshot:
            return self.get_default_state()

        return most_recent_state_snapshot

    def get_most_recent_state(self) -> StateType:
        most_recent_state_snapshot: Optional[StateType] = None

        for snapshot in self._store.state_snapshots:
            next_state = cast(StateType, snapshot)
            if not most_recent_state_snapshot:
                most_recent_state_snapshot = next_state
            elif next_state.meta.updated_ts >= most_recent_state_snapshot.meta.updated_ts:
                most_recent_state_snapshot = next_state

        if not most_recent_state_snapshot:
            return self.get_default_state()

        return most_recent_state_snapshot

    @staticmethod
    def load_from_module(module_path: str) -> Type["BaseWorkflow"]:
        workflow_path = f"{module_path}.workflow"
        module = importlib.import_module(workflow_path)

        workflows: List[Type[BaseWorkflow]] = []
        for name in dir(module):
            attr = getattr(module, name)
            if (
                inspect.isclass(attr)
                and issubclass(attr, BaseWorkflow)
                and attr != BaseWorkflow
                and attr.__module__ == workflow_path
            ):
                workflows.append(attr)

        if len(workflows) == 0:
            raise ValueError(f"No workflows found in {module_path}")
        elif len(workflows) > 1:
            raise ValueError(f"Multiple workflows found in {module_path}")

        return workflows[0]


WorkflowExecutionInitiatedBody.model_rebuild()
WorkflowExecutionFulfilledBody.model_rebuild()
WorkflowExecutionRejectedBody.model_rebuild()
WorkflowExecutionPausedBody.model_rebuild()
WorkflowExecutionResumedBody.model_rebuild()
WorkflowExecutionStreamingBody.model_rebuild()

NodeExecutionInitiatedBody.model_rebuild()
NodeExecutionFulfilledBody.model_rebuild()
NodeExecutionRejectedBody.model_rebuild()
NodeExecutionPausedBody.model_rebuild()
NodeExecutionResumedBody.model_rebuild()
NodeExecutionStreamingBody.model_rebuild()

WorkflowExecutionInitiatedEvent.model_rebuild()
WorkflowExecutionFulfilledEvent.model_rebuild()
WorkflowExecutionRejectedEvent.model_rebuild()
WorkflowExecutionPausedEvent.model_rebuild()
WorkflowExecutionResumedEvent.model_rebuild()
WorkflowExecutionStreamingEvent.model_rebuild()

NodeExecutionInitiatedEvent.model_rebuild()
NodeExecutionFulfilledEvent.model_rebuild()
NodeExecutionRejectedEvent.model_rebuild()
NodeExecutionPausedEvent.model_rebuild()
NodeExecutionResumedEvent.model_rebuild()
NodeExecutionStreamingEvent.model_rebuild()
