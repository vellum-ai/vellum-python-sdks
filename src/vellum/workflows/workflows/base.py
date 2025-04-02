from datetime import datetime
from functools import lru_cache
import importlib
import inspect
from threading import Event as ThreadingEvent
from uuid import UUID, uuid4
from typing import (
    Any,
    Callable,
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
from vellum.workflows.errors import WorkflowError, WorkflowErrorCode
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
    WorkflowExecutionSnapshottedBody,
    WorkflowExecutionSnapshottedEvent,
    WorkflowExecutionStreamingBody,
    WorkflowExecutionStreamingEvent,
)
from vellum.workflows.graph import Graph
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.mocks import MockNodeExecutionArg
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.runner import WorkflowRunner
from vellum.workflows.runner.runner import ExternalInputsArg, RunFromNodeArg
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.state.store import Store
from vellum.workflows.types.generics import InputsType, StateType
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.event_filters import workflow_event_filter


class _BaseWorkflowMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        if "graph" not in dct:
            dct["graph"] = set()

        if "Outputs" in dct:
            outputs_class = dct["Outputs"]

            if not any(issubclass(base, BaseOutputs) for base in outputs_class.__bases__):
                parent_outputs_class = next(
                    (base.Outputs for base in bases if hasattr(base, "Outputs")),
                    BaseOutputs,  # Default to BaseOutputs only if no parent has Outputs
                )

                filtered_bases = tuple(base for base in outputs_class.__bases__ if base is not object)

                new_dct = {key: value for key, value in outputs_class.__dict__.items() if not key.startswith("__")}
                new_dct["__module__"] = dct["__module__"]

                dct["Outputs"] = type(
                    f"{name}.Outputs",
                    (parent_outputs_class,) + filtered_bases,
                    new_dct,
                )

        def collect_nodes(graph_item: Union[GraphAttribute, Set[GraphAttribute]]) -> Set[Type[BaseNode]]:
            nodes: Set[Type[BaseNode]] = set()
            if isinstance(graph_item, Graph):
                nodes.update(node for node in graph_item.nodes)
            elif isinstance(graph_item, set):
                for item in graph_item:
                    if isinstance(item, Graph):
                        nodes.update(node for node in item.nodes)
                    elif inspect.isclass(item) and issubclass(item, BaseNode):
                        nodes.add(item)
            elif inspect.isclass(graph_item) and issubclass(graph_item, BaseNode):
                nodes.add(graph_item)
            else:
                raise TypeError(f"Unexpected graph type: {graph_item.__class__}")
            return nodes

        graph_nodes = collect_nodes(dct.get("graph", set()))
        unused_nodes = collect_nodes(dct.get("unused_graphs", set()))

        overlap = graph_nodes & unused_nodes
        if overlap:
            node_names = [node.__name__ for node in overlap]
            raise ValueError(f"Node(s) {', '.join(node_names)} cannot appear in both graph and unused_graphs")

        cls = super().__new__(mcs, name, bases, dct)
        workflow_class = cast(Type["BaseWorkflow"], cls)
        workflow_class.__id__ = uuid4_from_hash(workflow_class.__qualname__)
        return workflow_class


GraphAttribute = Union[Type[BaseNode], Graph, Set[Type[BaseNode]], Set[Graph]]


class BaseWorkflow(Generic[InputsType, StateType], metaclass=_BaseWorkflowMeta):
    __id__: UUID = uuid4_from_hash(__qualname__)
    graph: ClassVar[GraphAttribute]
    unused_graphs: ClassVar[Set[GraphAttribute]]  # nodes or graphs that are defined but not used in the graph
    emitters: List[BaseWorkflowEmitter]
    resolvers: List[BaseWorkflowResolver]

    class Outputs(BaseOutputs):
        pass

    WorkflowEvent = Union[  # type: ignore
        GenericWorkflowEvent,
        WorkflowExecutionInitiatedEvent[InputsType],  # type: ignore[valid-type]
        WorkflowExecutionFulfilledEvent[Outputs],
        WorkflowExecutionSnapshottedEvent[StateType],  # type: ignore[valid-type]
    ]

    TerminalWorkflowEvent = Union[
        WorkflowExecutionFulfilledEvent[Outputs],
        WorkflowExecutionRejectedEvent,
        WorkflowExecutionPausedEvent,
    ]

    WorkflowEventStream = Generator[WorkflowEvent, None, None]

    def __init__(
        self,
        *,
        context: Optional[WorkflowContext] = None,
        parent_state: Optional[BaseState] = None,
        emitters: Optional[List[BaseWorkflowEmitter]] = None,
        resolvers: Optional[List[BaseWorkflowResolver]] = None,
        store: Optional[Store] = None,
    ):
        self._parent_state = parent_state
        self.emitters = emitters or (self.emitters if hasattr(self, "emitters") else [])
        self.resolvers = resolvers or (self.resolvers if hasattr(self, "resolvers") else [])
        self._context = context or WorkflowContext()
        self._store = store or Store()
        self._execution_context = self._context.execution_context

        self.validate()

    @property
    def context(self) -> WorkflowContext:
        return self._context

    @staticmethod
    def _resolve_graph(graph: GraphAttribute) -> List[Graph]:
        """
        Resolves a single graph source to a list of Graph objects.
        """
        if isinstance(graph, Graph):
            return [graph]
        if isinstance(graph, set):
            graphs = []
            for item in graph:
                if isinstance(item, Graph):
                    graphs.append(item)
                elif issubclass(item, BaseNode):
                    graphs.append(Graph.from_node(item))
                else:
                    raise ValueError(f"Unexpected graph type: {type(item)}")
            return graphs
        if issubclass(graph, BaseNode):
            return [Graph.from_node(graph)]
        raise ValueError(f"Unexpected graph type: {type(graph)}")

    @staticmethod
    def _get_edges_from_subgraphs(subgraphs: Iterable[Graph]) -> Iterator[Edge]:
        edges = set()
        for subgraph in subgraphs:
            for edge in subgraph.edges:
                if edge not in edges:
                    edges.add(edge)
                    yield edge

    @staticmethod
    def _get_nodes_from_subgraphs(subgraphs: Iterable[Graph]) -> Iterator[Type[BaseNode]]:
        nodes = set()
        for subgraph in subgraphs:
            for node in subgraph.nodes:
                if node not in nodes:
                    nodes.add(node)
                    yield node

    @classmethod
    def get_subgraphs(cls) -> List[Graph]:
        return cls._resolve_graph(cls.graph)

    @classmethod
    def get_edges(cls) -> Iterator[Edge]:
        """
        Returns an iterator over the edges in the workflow. We use a set to
        ensure uniqueness, and the iterator to preserve order.
        """
        return cls._get_edges_from_subgraphs(cls.get_subgraphs())

    @classmethod
    def get_nodes(cls) -> Iterator[Type[BaseNode]]:
        """
        Returns an iterator over the nodes in the workflow. We use a set to
        ensure uniqueness, and the iterator to preserve order.
        """
        return cls._get_nodes_from_subgraphs(cls.get_subgraphs())

    @classmethod
    def get_unused_subgraphs(cls) -> List[Graph]:
        """
        Returns a list of subgraphs that are defined but not used in the graph
        """
        if not hasattr(cls, "unused_graphs"):
            return []
        graphs = []
        for item in cls.unused_graphs:
            graphs.extend(cls._resolve_graph(item))
        return graphs

    @classmethod
    def get_unused_nodes(cls) -> Iterator[Type[BaseNode]]:
        """
        Returns an iterator over the nodes that are defined but not used in the graph.
        """
        return cls._get_nodes_from_subgraphs(cls.get_unused_subgraphs())

    @classmethod
    def get_unused_edges(cls) -> Iterator[Edge]:
        """
        Returns an iterator over edges that are defined but not used in the graph.
        """
        return cls._get_edges_from_subgraphs(cls.get_unused_subgraphs())

    @classmethod
    def get_entrypoints(cls) -> Iterable[Type[BaseNode]]:
        return iter({e for g in cls.get_subgraphs() for e in g.entrypoints})

    def run(
        self,
        inputs: Optional[InputsType] = None,
        *,
        state: Optional[StateType] = None,
        entrypoint_nodes: Optional[RunFromNodeArg] = None,
        external_inputs: Optional[ExternalInputsArg] = None,
        cancel_signal: Optional[ThreadingEvent] = None,
        node_output_mocks: Optional[MockNodeExecutionArg] = None,
        max_concurrency: Optional[int] = None,
    ) -> TerminalWorkflowEvent:
        """
        Invoke a Workflow, returning the last event emitted, which should be one of:
        - `WorkflowExecutionFulfilledEvent` if the Workflow Execution was successful
        - `WorkflowExecutionRejectedEvent` if the Workflow Execution was rejected
        - `WorkflowExecutionPausedEvent` if the Workflow Execution was paused

        Parameters
        ----------
        inputs: Optional[InputsType] = None
            The Inputs instance used to initiate the Workflow Execution.

        state: Optional[StateType] = None
            The State instance to run the Workflow with. Workflows maintain a global state that can be used to
            deterministically resume execution from any point.

        entrypoint_nodes: Optional[RunFromNodeArg] = None
            The entrypoint nodes to run the Workflow with. Useful for resuming execution from a specific node.

        external_inputs: Optional[ExternalInputsArg] = None
            External inputs to pass to the Workflow. Useful for providing human-in-the-loop behavior to the Workflow.

        cancel_signal: Optional[ThreadingEvent] = None
            A threading event that can be used to cancel the Workflow Execution.

        node_output_mocks: Optional[MockNodeExecutionArg] = None
            A list of Outputs to mock for Nodes during Workflow Execution. Each mock can include a `when_condition`
            that must be met for the mock to be used.

        max_concurrency: Optional[int] = None
            The max number of concurrent threads to run the Workflow with. If not provided, the Workflow will run
            without limiting concurrency. This configuration only applies to the current Workflow and not to any
            subworkflows or nodes that utilizes threads.
        """

        events = WorkflowRunner(
            self,
            inputs=inputs,
            state=state,
            entrypoint_nodes=entrypoint_nodes,
            external_inputs=external_inputs,
            cancel_signal=cancel_signal,
            node_output_mocks=node_output_mocks,
            max_concurrency=max_concurrency,
            init_execution_context=self._execution_context,
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
                    error=WorkflowError(
                        code=WorkflowErrorCode.INTERNAL_ERROR,
                        message="No events were emitted",
                    ),
                    workflow_definition=self.__class__,
                ),
            )

        if not first_event:
            return WorkflowExecutionRejectedEvent(
                trace_id=uuid4(),
                span_id=uuid4(),
                body=WorkflowExecutionRejectedBody(
                    error=WorkflowError(
                        code=WorkflowErrorCode.INTERNAL_ERROR,
                        message="Initiated event was never emitted",
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
                error=WorkflowError(
                    code=WorkflowErrorCode.INTERNAL_ERROR,
                    message=f"Unexpected last event name found: {last_event.name}",
                ),
            ),
        )

    def stream(
        self,
        inputs: Optional[InputsType] = None,
        *,
        event_filter: Optional[Callable[[Type["BaseWorkflow"], WorkflowEvent], bool]] = None,
        state: Optional[StateType] = None,
        entrypoint_nodes: Optional[RunFromNodeArg] = None,
        external_inputs: Optional[ExternalInputsArg] = None,
        cancel_signal: Optional[ThreadingEvent] = None,
        node_output_mocks: Optional[MockNodeExecutionArg] = None,
        max_concurrency: Optional[int] = None,
    ) -> WorkflowEventStream:
        """
        Invoke a Workflow, yielding events as they are emitted.

        Parameters
        ----------
        event_filter: Optional[Callable[[Type["BaseWorkflow"], WorkflowEvent], bool]] = None
            A filter that can be used to filter events based on the Workflow Class and the event itself. If the method
            returns `False`, the event will not be yielded.

        inputs: Optional[InputsType] = None
            The Inputs instance used to initiate the Workflow Execution.

        state: Optional[StateType] = None
            The State instance to run the Workflow with. Workflows maintain a global state that can be used to
            deterministically resume execution from any point.

        entrypoint_nodes: Optional[RunFromNodeArg] = None
            The entrypoint nodes to run the Workflow with. Useful for resuming execution from a specific node.

        external_inputs: Optional[ExternalInputsArg] = None
            External inputs to pass to the Workflow. Useful for providing human-in-the-loop behavior to the Workflow.

        cancel_signal: Optional[ThreadingEvent] = None
            A threading event that can be used to cancel the Workflow Execution.

        node_output_mocks: Optional[MockNodeExecutionArg] = None
            A list of Outputs to mock for Nodes during Workflow Execution. Each mock can include a `when_condition`
            that must be met for the mock to be used.

        max_concurrency: Optional[int] = None
            The max number of concurrent threads to run the Workflow with. If not provided, the Workflow will run
            without limiting concurrency. This configuration only applies to the current Workflow and not to any
            subworkflows or nodes that utilizes threads.
        """

        should_yield = event_filter or workflow_event_filter
        for event in WorkflowRunner(
            self,
            inputs=inputs,
            state=state,
            entrypoint_nodes=entrypoint_nodes,
            external_inputs=external_inputs,
            cancel_signal=cancel_signal,
            node_output_mocks=node_output_mocks,
            max_concurrency=max_concurrency,
            init_execution_context=self._execution_context,
        ).stream():
            if should_yield(self.__class__, event):
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
    def _get_parameterized_classes(
        cls,
    ) -> Tuple[Type[InputsType], Type[StateType]]:
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
    def get_inputs_class(cls) -> Type[InputsType]:
        return cls._get_parameterized_classes()[0]

    @classmethod
    def get_state_class(cls) -> Type[StateType]:
        return cls._get_parameterized_classes()[1]

    def get_default_inputs(self) -> InputsType:
        return self.get_inputs_class()()

    def get_default_state(self, workflow_inputs: Optional[InputsType] = None) -> StateType:
        execution_context = self._execution_context
        return self.get_state_class()(
            meta=(
                StateMeta(
                    parent=self._parent_state,
                    workflow_inputs=workflow_inputs or self.get_default_inputs(),
                    trace_id=execution_context.trace_id,
                )
                if execution_context and int(execution_context.trace_id)
                else StateMeta(
                    parent=self._parent_state,
                    workflow_inputs=workflow_inputs or self.get_default_inputs(),
                )
            )
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
            if name.startswith("__"):
                continue

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
WorkflowExecutionSnapshottedBody.model_rebuild()

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
WorkflowExecutionSnapshottedEvent.model_rebuild()

NodeExecutionInitiatedEvent.model_rebuild()
NodeExecutionFulfilledEvent.model_rebuild()
NodeExecutionRejectedEvent.model_rebuild()
NodeExecutionPausedEvent.model_rebuild()
NodeExecutionResumedEvent.model_rebuild()
NodeExecutionStreamingEvent.model_rebuild()
