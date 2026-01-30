from dataclasses import field
from datetime import datetime
from functools import lru_cache
import importlib
import inspect
import logging
import sys
import traceback
from uuid import UUID, uuid4
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
    overload,
)

if TYPE_CHECKING:
    from vellum.workflows.inputs.dataset_row import DatasetRow

from pydantic import ValidationError

from vellum.utils.uuid import is_valid_uuid
from vellum.workflows.edges import Edge
from vellum.workflows.emitters.base import BaseWorkflowEmitter
from vellum.workflows.errors import WorkflowError, WorkflowErrorCode
from vellum.workflows.events.node import (
    NodeEvent,
    NodeExecutionFulfilledBody,
    NodeExecutionFulfilledEvent,
    NodeExecutionInitiatedBody,
    NodeExecutionInitiatedEvent,
    NodeExecutionLogBody,
    NodeExecutionLogEvent,
    NodeExecutionPausedBody,
    NodeExecutionPausedEvent,
    NodeExecutionRejectedBody,
    NodeExecutionRejectedEvent,
    NodeExecutionResumedBody,
    NodeExecutionResumedEvent,
    NodeExecutionStreamingBody,
    NodeExecutionStreamingEvent,
)
from vellum.workflows.events.stream import WorkflowEventGenerator
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
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.executable import BaseExecutable
from vellum.workflows.graph import Graph
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.loaders.base import BaseWorkflowFinder
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.mocks import MockNodeExecutionArg
from vellum.workflows.nodes.utils import get_unadorned_node
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.ports import Port
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.runner import WorkflowRunner
from vellum.workflows.runner.runner import ExternalInputsArg, RunFromNodeArg
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.state.store import Store
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.types import CancelSignal
from vellum.workflows.types.generics import InputsType, StateType
from vellum.workflows.types.utils import get_original_base
from vellum.workflows.utils.module_path import normalize_module_path
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.event_filters import workflow_event_filter

logger = logging.getLogger(__name__)


class _BaseWorkflowMeta(type):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        if "graph" not in dct:
            dct["graph"] = set()
            for base in bases:
                base_graph = getattr(base, "graph", None)
                if base_graph:
                    dct["graph"] = base_graph
                    break

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
            elif isinstance(graph_item, Port):
                nodes.add(graph_item.node_class)
            elif isinstance(graph_item, set):
                for item in graph_item:
                    if isinstance(item, Graph):
                        nodes.update(node for node in item.nodes)
                    elif isinstance(item, Port):
                        nodes.add(item.node_class)
                    elif inspect.isclass(item) and issubclass(item, BaseNode):
                        nodes.add(item)
            elif inspect.isclass(graph_item) and issubclass(graph_item, BaseNode):
                nodes.add(graph_item)
            else:
                raise TypeError(f"Unexpected graph type: {graph_item.__class__}")
            return nodes

        def filter_overlapping_nodes_from_unused_graphs(
            unused_graphs: Set[GraphAttribute], overlapping_nodes: Set[Type[BaseNode]]
        ) -> Set[GraphAttribute]:
            filtered_graphs: Set[GraphAttribute] = set()

            for item in unused_graphs:
                if isinstance(item, Graph):
                    graph_nodes = set(item.nodes)
                    overlapping_in_graph = graph_nodes & overlapping_nodes

                    if not overlapping_in_graph:
                        filtered_graphs.add(item)
                    else:
                        non_overlapping_nodes = graph_nodes - overlapping_nodes
                        for node in non_overlapping_nodes:
                            filtered_graphs.add(node)

                elif isinstance(item, Port):
                    if item.node_class not in overlapping_nodes:
                        filtered_graphs.add(item)

                elif isinstance(item, set):
                    filtered_nodes: Set[Type[BaseNode]] = set()
                    filtered_graphs_in_set: Set[Graph] = set()
                    filtered_ports_in_set: Set[Port] = set()

                    for subitem in item:
                        if isinstance(subitem, Graph):
                            graph_nodes = set(subitem.nodes)
                            overlapping_in_graph = graph_nodes & overlapping_nodes

                            if not overlapping_in_graph:
                                filtered_graphs_in_set.add(subitem)
                            else:
                                non_overlapping_nodes = graph_nodes - overlapping_nodes
                                filtered_nodes.update(non_overlapping_nodes)
                        elif isinstance(subitem, Port):
                            if subitem.node_class not in overlapping_nodes:
                                filtered_ports_in_set.add(subitem)
                        elif isinstance(subitem, type) and issubclass(subitem, BaseNode):
                            if subitem not in overlapping_nodes:
                                filtered_nodes.add(subitem)
                        else:
                            raise TypeError(f"Unexpected item type in unused_graphs set: {subitem.__class__}")

                    # Add non-empty sets back to filtered_graphs
                    if filtered_nodes:
                        filtered_graphs.add(filtered_nodes)
                    if filtered_graphs_in_set:
                        filtered_graphs.add(filtered_graphs_in_set)
                    if filtered_ports_in_set:
                        filtered_graphs.add(filtered_ports_in_set)

                elif isinstance(item, type) and issubclass(item, BaseNode):
                    if item not in overlapping_nodes:
                        filtered_graphs.add(item)
                else:
                    filtered_graphs.add(item)

            return filtered_graphs

        graph_nodes = collect_nodes(dct.get("graph", set()))
        unused_nodes = collect_nodes(dct.get("unused_graphs", set()))

        overlap = graph_nodes & unused_nodes
        if overlap:
            node_names = [node.__name__ for node in overlap]
            logger.warning(
                f"Node(s) {', '.join(node_names)} appear in both graph and unused_graphs. Removing from unused_graphs."
            )

            # Filter out overlapping nodes from unused_graphs
            if "unused_graphs" in dct:
                dct["unused_graphs"] = filter_overlapping_nodes_from_unused_graphs(dct["unused_graphs"], overlap)

        cls = super().__new__(mcs, name, bases, dct)
        workflow_class = cast(Type["BaseWorkflow"], cls)
        workflow_class.__id__ = uuid4_from_hash(workflow_class.__qualname__)

        inputs_class = workflow_class.get_inputs_class()
        if inputs_class is not BaseInputs and inputs_class.__parent_class__ is type(None):
            inputs_class.__parent_class__ = workflow_class

        workflow_class.Outputs.__parent_class__ = workflow_class
        workflow_class.__output_ids__ = {
            ref.name: uuid4_from_hash(f"{workflow_class.__id__}|id|{ref.name}") for ref in workflow_class.Outputs
        }

        return workflow_class


GraphAttribute = Union[Type[BaseNode], Graph, Port, Set[Type[BaseNode]], Set[Graph], Set[Port]]


class BaseWorkflow(Generic[InputsType, StateType], BaseExecutable, metaclass=_BaseWorkflowMeta):
    graph: ClassVar[GraphAttribute]
    unused_graphs: ClassVar[Set[GraphAttribute]]  # nodes or graphs that are defined but not used in the graph
    emitters: List[BaseWorkflowEmitter]
    resolvers: List[BaseWorkflowResolver]
    is_dynamic: ClassVar[bool] = False

    class Display:
        """Optional display metadata for visual representation."""

        layout: Optional[Literal["auto"]] = None

    class Outputs(BaseOutputs):
        __parent_class__: Type["BaseWorkflow"] = field(init=False)

    WorkflowEvent = Union[  # type: ignore
        GenericWorkflowEvent,
        WorkflowExecutionInitiatedEvent[InputsType, StateType],  # type: ignore[valid-type]
        WorkflowExecutionFulfilledEvent[Outputs, StateType],  # type: ignore[valid-type]
        WorkflowExecutionSnapshottedEvent[StateType],  # type: ignore[valid-type]
    ]

    TerminalWorkflowEvent = Union[
        WorkflowExecutionFulfilledEvent[Outputs, StateType],  # type: ignore[valid-type]
        WorkflowExecutionRejectedEvent,
        WorkflowExecutionPausedEvent,
    ]

    WorkflowEventStream = WorkflowEventGenerator[WorkflowEvent]

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
        self._context = context or WorkflowContext()
        self.emitters = emitters or (self.emitters if hasattr(self, "emitters") else [])
        self.resolvers = resolvers or (self.resolvers if hasattr(self, "resolvers") else [])
        # Prioritize store type from WorkflowContext to allow subworkflows to inherit EmptyStore
        # TODO(v2.0.0): Remove the concept of an internal store altogether (important-comment)
        self._store = store or self._context.store_class()
        self._execution_context = self._context.execution_context
        self._current_runner: Optional[WorkflowRunner] = None

        # Register context with all emitters
        for emitter in self.emitters:
            emitter.register_context(self._context)

        for resolver in self.resolvers:
            resolver.register_workflow_instance(self)

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
        if isinstance(graph, Port):
            return [Graph.from_port(graph)]
        if isinstance(graph, set):
            graphs = []
            for item in graph:
                if isinstance(item, Graph):
                    graphs.append(item)
                elif isinstance(item, Port):
                    graphs.append(Graph.from_port(item))
                elif inspect.isclass(item) and issubclass(item, BaseNode):
                    graphs.append(Graph.from_node(item))
                else:
                    raise ValueError(f"Unexpected graph type: {type(item)}")
            return graphs
        if inspect.isclass(graph) and issubclass(graph, BaseNode):
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
    def get_all_nodes(cls) -> Iterator[Type[BaseNode]]:
        """
        Returns an iterator over all nodes in the Workflow, used or unused.
        """
        yield from cls.get_nodes()
        yield from cls.get_unused_nodes()

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
        previous_execution_id: Optional[Union[str, UUID]] = None,
        execution_id: Optional[UUID] = None,
        cancel_signal: Optional[CancelSignal] = None,
        node_output_mocks: Optional[MockNodeExecutionArg] = None,
        max_concurrency: Optional[int] = None,
        timeout: Optional[float] = None,
        trigger: Optional[BaseTrigger] = None,
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

        previous_execution_id: Optional[Union[str, UUID]] = None
            The execution ID of the previous execution to resume from.

        execution_id: Optional[UUID] = None
            The execution ID to use for this workflow run. Sets the initial state's span_id for fresh runs.

        cancel_signal: Optional[CancelSignal] = None
            A cancel signal that can be used to cancel the Workflow Execution.

        node_output_mocks: Optional[MockNodeExecutionArg] = None
            A list of Outputs to mock for Nodes during Workflow Execution. Each mock can include a `when_condition`
            that must be met for the mock to be used.

        max_concurrency: Optional[int] = None
            The max number of concurrent threads to run the Workflow with. If not provided, the Workflow will run
            without limiting concurrency. This configuration only applies to the current Workflow and not to any
            subworkflows or nodes that utilizes threads.

        timeout: Optional[float] = None
            The maximum time in seconds to allow the Workflow to run. If the timeout is exceeded, the Workflow
            will be rejected with a WORKFLOW_TIMEOUT error code and any nodes in flight will be rejected.

        trigger: Optional[BaseTrigger] = None
            A trigger instance for workflows with triggers (e.g., IntegrationTrigger, ManualTrigger, ScheduledTrigger).
            The trigger instance is bound to the workflow state, making its attributes accessible to downstream nodes.
            Required for workflows that only have IntegrationTrigger; optional for workflows with both ManualTrigger
            and IntegrationTrigger.
        """

        runner = WorkflowRunner(
            self,
            inputs=inputs,
            state=state,
            entrypoint_nodes=entrypoint_nodes,
            external_inputs=external_inputs,
            previous_execution_id=previous_execution_id,
            cancel_signal=cancel_signal,
            node_output_mocks=node_output_mocks,
            max_concurrency=max_concurrency,
            timeout=timeout,
            init_execution_context=self._execution_context,
            trigger=trigger,
            execution_id=execution_id,
        )
        self._current_runner = runner
        events = runner.stream()
        first_event: Optional[Union[WorkflowExecutionInitiatedEvent, WorkflowExecutionResumedEvent]] = None
        last_event = None
        for event in events:
            if event.name == "workflow.execution.initiated" or event.name == "workflow.execution.resumed":
                first_event = event
            last_event = event

        if not last_event:
            rejected_event = WorkflowExecutionRejectedEvent(
                trace_id=self._execution_context.trace_id,
                span_id=uuid4(),
                body=WorkflowExecutionRejectedBody(
                    error=WorkflowError(
                        code=WorkflowErrorCode.INTERNAL_ERROR,
                        message="No events were emitted",
                    ),
                    workflow_definition=self.__class__,
                ),
            )
            return rejected_event

        if not first_event:
            rejected_event = WorkflowExecutionRejectedEvent(
                trace_id=self._execution_context.trace_id,
                span_id=uuid4(),
                body=WorkflowExecutionRejectedBody(
                    error=WorkflowError(
                        code=WorkflowErrorCode.INTERNAL_ERROR,
                        message="Initiated event was never emitted",
                    ),
                    workflow_definition=self.__class__,
                ),
            )
            return rejected_event

        if (
            last_event.name == "workflow.execution.rejected"
            or last_event.name == "workflow.execution.fulfilled"
            or last_event.name == "workflow.execution.paused"
        ):
            return last_event

        rejected_event = WorkflowExecutionRejectedEvent(
            trace_id=self._execution_context.trace_id,
            span_id=first_event.span_id,
            body=WorkflowExecutionRejectedBody(
                workflow_definition=self.__class__,
                error=WorkflowError(
                    code=WorkflowErrorCode.INTERNAL_ERROR,
                    message=f"Unexpected last event name found: {last_event.name}",
                ),
            ),
        )
        return rejected_event

    def stream(
        self,
        inputs: Optional[InputsType] = None,
        *,
        event_filter: Optional[Callable[[Type["BaseWorkflow"], WorkflowEvent], bool]] = None,
        state: Optional[StateType] = None,
        entrypoint_nodes: Optional[RunFromNodeArg] = None,
        external_inputs: Optional[ExternalInputsArg] = None,
        previous_execution_id: Optional[Union[str, UUID]] = None,
        execution_id: Optional[UUID] = None,
        cancel_signal: Optional[CancelSignal] = None,
        node_output_mocks: Optional[MockNodeExecutionArg] = None,
        max_concurrency: Optional[int] = None,
        timeout: Optional[float] = None,
        trigger: Optional[BaseTrigger] = None,
        event_max_size: Optional[int] = None,
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

        previous_execution_id: Optional[Union[str, UUID]] = None
            The execution ID of the previous execution to resume from.

        execution_id: Optional[UUID] = None
            The execution ID to use for this workflow run. Sets the initial state's span_id for fresh runs.

        cancel_signal: Optional[CancelSignal] = None
            A cancel signal that can be used to cancel the Workflow Execution.

        node_output_mocks: Optional[MockNodeExecutionArg] = None
            A list of Outputs to mock for Nodes during Workflow Execution. Each mock can include a `when_condition`
            that must be met for the mock to be used.

        max_concurrency: Optional[int] = None
            The max number of concurrent threads to run the Workflow with. If not provided, the Workflow will run
            without limiting concurrency. This configuration only applies to the current Workflow and not to any
            subworkflows or nodes that utilizes threads.

        timeout: Optional[float] = None
            The maximum time in seconds to allow the Workflow to run. If the timeout is exceeded, the Workflow
            will be rejected with a WORKFLOW_TIMEOUT error code and any nodes in flight will be rejected.

        trigger: Optional[BaseTrigger] = None
            A trigger instance for workflows with triggers (e.g., IntegrationTrigger, ManualTrigger, ScheduledTrigger).
            The trigger instance is bound to the workflow state, making its attributes accessible to downstream nodes.
            Required for workflows that only have IntegrationTrigger; optional for workflows with both ManualTrigger
            and IntegrationTrigger.

        event_max_size: Optional[int] = None
            The maximum size in bytes for serialized events. If an event's serialized size exceeds this value,
            the outputs will be set to an empty dict.
        """

        should_yield = event_filter or workflow_event_filter
        runner = WorkflowRunner(
            self,
            inputs=inputs,
            state=state,
            entrypoint_nodes=entrypoint_nodes,
            external_inputs=external_inputs,
            previous_execution_id=previous_execution_id,
            cancel_signal=cancel_signal,
            node_output_mocks=node_output_mocks,
            max_concurrency=max_concurrency,
            timeout=timeout,
            init_execution_context=self._execution_context,
            trigger=trigger,
            execution_id=execution_id,
            event_max_size=event_max_size,
        )
        self._current_runner = runner
        runner_stream = runner.stream()

        def _generate_filtered_events() -> Generator[BaseWorkflow.WorkflowEvent, None, None]:
            for event in runner_stream:
                if should_yield(self.__class__, event):
                    yield event

        return WorkflowEventGenerator(_generate_filtered_events(), runner_stream.span_id)

    @classmethod
    def validate(cls) -> None:
        """
        Validates the Workflow, by running through our list of linter rules.
        """

        cls._validate_no_self_edges()

    @classmethod
    def get_all_nodes_recursive(cls) -> Iterator[Type[BaseNode]]:
        """
        Returns an iterator over all nodes in the Workflow, including nodes nested in subworkflows.
        """
        for node in cls.get_all_nodes():
            yield node
            for node_ref in node:
                attr_value = node_ref.instance
                if inspect.isclass(attr_value) and issubclass(attr_value, BaseWorkflow):
                    yield from attr_value.get_all_nodes_recursive()

    @classmethod
    def resolve_node_ref(cls, node_ref: Union[Type[BaseNode], UUID, str]) -> Type[BaseNode]:
        """
        Resolve a node reference (class, UUID, or string) to a node class.

        Args:
            node_ref: Either a node class, a UUID, or a fully qualified string
                     in the format "module.ClassName"

        Returns:
            The resolved node class

        Raises:
            WorkflowInitializationException: If the node reference cannot be resolved
        """
        if inspect.isclass(node_ref) and issubclass(node_ref, BaseNode):
            return node_ref

        candidate_nodes: List[Type[BaseNode]] = []
        for node in cls.get_all_nodes_recursive():
            candidate_nodes.append(node)
            wrapped_node = get_unadorned_node(node)
            if wrapped_node != node:
                candidate_nodes.append(wrapped_node)

        if isinstance(node_ref, UUID):
            node_uuid = node_ref
        elif is_valid_uuid(node_ref):
            node_uuid = UUID(node_ref)
        else:
            node_uuid = None

        if node_uuid:
            for node in candidate_nodes:
                if node.__id__ == node_uuid:
                    return node
            raise WorkflowInitializationException(
                message=f"Node '{node_uuid}' not found in workflow",
                raw_data={"node_ref": str(node_uuid)},
            )

        if isinstance(node_ref, str):
            try:
                module_path, class_name = node_ref.rsplit(".", 1)
                module = importlib.import_module(module_path)
                node_class = getattr(module, class_name)
                if inspect.isclass(node_class) and issubclass(node_class, BaseNode):
                    return node_class
                raise WorkflowInitializationException(
                    message=f"Node '{node_ref}' not found in workflow",
                    raw_data={"node_ref": node_ref},
                )
            except (ValueError, ModuleNotFoundError, AttributeError):
                for node in candidate_nodes:
                    full_path = f"{node.__module__}.{node.__name__}"
                    # Normalize the path to strip ephemeral namespace prefix from dynamically loaded workflows
                    normalized_path = normalize_module_path(full_path)
                    if normalized_path == node_ref:
                        return node
                raise WorkflowInitializationException(
                    message=f"Node '{node_ref}' not found in workflow",
                    raw_data={"node_ref": node_ref},
                )

        raise WorkflowInitializationException(
            message=f"Node '{node_ref}' not found in workflow",
            raw_data={"node_ref": str(node_ref)},
        )

    def run_node(
        self, node: Union[Type[BaseNode], UUID, str], *, inputs: Optional[Dict[str, Any]] = None
    ) -> Generator[NodeEvent, None, None]:
        """
        Execute a single node and yield node execution events.

        Args:
            node: Either a node class, a UUID, or a fully qualified string
                 in the format "module.ClassName"
            inputs: Optional inputs to pass to the node

        Yields:
            NodeEvent: Events emitted during node execution

        Raises:
            ValueError: If the node reference cannot be resolved
        """
        resolved_node = self.resolve_node_ref(node)
        runner = WorkflowRunner(self)
        span_id = uuid4()
        node_instance = resolved_node(state=self.get_default_state(), context=self._context, inputs=inputs)

        return runner.run_node(node=node_instance, span_id=span_id)

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

    def get_default_state(
        self,
        workflow_inputs: Optional[InputsType] = None,
        execution_id: Optional[UUID] = None,
        *,
        trigger_attributes: Optional[Dict[TriggerAttributeReference, Any]] = None,
    ) -> StateType:
        resolved_inputs: Optional[InputsType] = workflow_inputs

        meta_payload: Dict[str, Any] = {
            "parent": self._parent_state,
            "workflow_definition": self.__class__,
            "workflow_inputs": resolved_inputs,
        }
        if trigger_attributes is not None:
            meta_payload["trigger_attributes"] = trigger_attributes

        meta = StateMeta.model_validate(
            meta_payload,
            context={
                "workflow_definition": self.__class__,
            },
        )

        # Makes the uuid factory mocker work this way instead of setting in cosntructor
        if execution_id:
            meta.span_id = execution_id

        return self.get_state_class()(meta=meta)

    def get_state_at_node(self, node: Type[BaseNode], execution_id: Optional[UUID] = None) -> StateType:
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
            return self.get_default_state(execution_id=execution_id)

        return most_recent_state_snapshot

    def get_most_recent_state(self, execution_id: Optional[UUID] = None) -> StateType:
        most_recent_state_snapshot: Optional[StateType] = None

        for snapshot in self._store.state_snapshots:
            next_state = cast(StateType, snapshot)
            if not most_recent_state_snapshot:
                most_recent_state_snapshot = next_state
            elif next_state.meta.updated_ts >= most_recent_state_snapshot.meta.updated_ts:
                most_recent_state_snapshot = next_state

        if not most_recent_state_snapshot:
            return self.get_default_state(execution_id=execution_id)

        return most_recent_state_snapshot

    @overload
    @classmethod
    def deserialize_state(cls, state: dict, workflow_inputs: Optional[InputsType] = None) -> StateType: ...

    @overload
    @classmethod
    def deserialize_state(cls, state: None, workflow_inputs: Optional[InputsType] = None) -> None: ...

    @classmethod
    def deserialize_state(
        cls, state: Optional[dict], workflow_inputs: Optional[InputsType] = None
    ) -> Optional[StateType]:
        if state is None:
            return None

        state_class = cls.get_state_class()
        if "meta" in state:
            meta_payload = dict(state["meta"])
            if workflow_inputs is not None:
                meta_payload["workflow_inputs"] = workflow_inputs
            meta_payload.setdefault("workflow_definition", cls)

            state["meta"] = StateMeta.model_validate(
                meta_payload,
                context={
                    "workflow_definition": cls,
                },
            )

        return state_class(**state)

    @classmethod
    def _resolve_dataset_row(
        cls,
        dataset_row: Union[int, str, UUID],
    ) -> "DatasetRow":
        """
        Resolve a dataset row selector by loading the sandbox module and finding the matching row.

        Parameters
        ----------
        dataset_row: Union[int, str, UUID]
            The dataset row selector. Can be an int (index), str (label), or UUID (id).

        Returns
        -------
        DatasetRow
            The resolved dataset row.

        Raises
        ------
        WorkflowInitializationException
            If the sandbox module cannot be loaded, dataset is not found, or selector doesn't match.
        """
        # Import here to avoid circular imports
        from vellum.workflows.inputs.dataset_row import DatasetRow

        # Derive sandbox module path from workflow class module
        # cls.__module__ is like "tests.workflows.test_dataset_row_resolution.workflow"
        # We need "tests.workflows.test_dataset_row_resolution.sandbox"
        workflow_module = cls.__module__
        if workflow_module.endswith(".workflow"):
            sandbox_module_path = workflow_module[:-9] + ".sandbox"  # Replace ".workflow" with ".sandbox"
        else:
            # Fallback: assume sandbox is a sibling module
            parts = workflow_module.rsplit(".", 1)
            sandbox_module_path = parts[0] + ".sandbox" if len(parts) > 1 else "sandbox"

        try:
            sandbox_module = importlib.import_module(sandbox_module_path)
        except Exception as e:
            raise WorkflowInitializationException(
                message=f"Could not load sandbox module '{sandbox_module_path}': {e}",
                workflow_definition=cls,
            ) from e

        dataset = getattr(sandbox_module, "dataset", None)
        if dataset is None:
            raise WorkflowInitializationException(
                message=f"Sandbox module '{sandbox_module_path}' does not have a 'dataset' variable",
                workflow_definition=cls,
            )

        # Validate that dataset is a list
        if not isinstance(dataset, list):
            raise WorkflowInitializationException(
                message=f"Sandbox module '{sandbox_module_path}' dataset must be a list, got {type(dataset).__name__}",
                workflow_definition=cls,
            )

        # Get the workflow's inputs class for validation
        inputs_class = cls.get_inputs_class()

        # Resolve the dataset row
        if isinstance(dataset_row, int):
            if dataset_row < 0 or dataset_row >= len(dataset):
                raise WorkflowInitializationException(
                    message=f"Dataset row index {dataset_row} is out of bounds (dataset has {len(dataset)} rows)",
                    workflow_definition=cls,
                )
            row = dataset[dataset_row]
            if isinstance(row, DatasetRow):
                return row
            elif isinstance(row, inputs_class):
                return DatasetRow(label=f"Scenario {dataset_row + 1}", inputs=row)
            else:
                raise WorkflowInitializationException(
                    message=f"Dataset row at index {dataset_row} must be a DatasetRow or {inputs_class.__name__}, "
                    f"got {type(row).__name__}",
                    workflow_definition=cls,
                )

        # For string selectors, check if it's a valid UUID first
        if isinstance(dataset_row, str) and is_valid_uuid(dataset_row):
            dataset_row = UUID(dataset_row)

        selector_str = str(dataset_row) if isinstance(dataset_row, UUID) else dataset_row

        for i, row in enumerate(dataset):
            if isinstance(row, DatasetRow):
                if isinstance(dataset_row, UUID) and row.id == selector_str:
                    return row
                if isinstance(dataset_row, str) and row.label == dataset_row:
                    return row
            elif isinstance(row, inputs_class):
                # BaseInputs case - match by default label
                default_label = f"Scenario {i + 1}"
                if isinstance(dataset_row, str) and default_label == dataset_row:
                    return DatasetRow(label=default_label, inputs=row)

        if isinstance(dataset_row, UUID):
            raise WorkflowInitializationException(
                message=f"No dataset row found with id '{selector_str}'",
                workflow_definition=cls,
            )
        raise WorkflowInitializationException(
            message=f"No dataset row found with label '{dataset_row}'",
            workflow_definition=cls,
        )

    @classmethod
    def deserialize_trigger(
        cls,
        trigger_id: Optional[Union[str, UUID]],
        inputs: dict,
        dataset_row: Optional[Union[int, str, UUID]] = None,
    ) -> Union[InputsType, BaseTrigger]:
        """
        Deserialize a trigger from a trigger_id and inputs dict.

        If trigger_id is None, returns an instance of the workflow's Inputs class.
        Otherwise, finds a trigger class that matches the trigger_id and creates an instance of that.

        When dataset_row is provided, the method loads the sandbox module, resolves the dataset row,
        and uses the row's inputs for instantiation.

        Parameters
        ----------
        trigger_id: Optional[Union[str, UUID]]
            The identifier of the trigger class to instantiate. Can be:
            - None: Returns workflow Inputs
            - UUID: Matches by trigger class __id__
            - str (valid UUID): Matches by trigger class __id__
            - str (non-UUID): Matches by trigger name (from __trigger_name__)

        inputs: dict
            The inputs to pass to the trigger or Inputs constructor.

        dataset_row: Optional[Union[int, str, UUID]]
            Optional dataset row selector. Can be an int (index), str (label), or UUID (id).
            When provided, the sandbox module is loaded and the matching dataset row's inputs
            are used for instantiation.

        Returns
        -------
        Union[InputsType, BaseTrigger]
            Either an instance of the workflow's Inputs class (if trigger_id is None)
            or an instance of the matching trigger class.

        Raises
        ------
        WorkflowInitializationException
            If trigger_id is provided but no matching trigger class is found in the workflow,
            or if dataset_row is provided but cannot be resolved.
        """
        # Resolve dataset row if provided
        resolved_inputs = inputs
        if dataset_row is not None:
            resolved_row = cls._resolve_dataset_row(dataset_row)

            # If the dataset row has a workflow_trigger, return it immediately
            if resolved_row.workflow_trigger is not None:
                return resolved_row.workflow_trigger

            # Otherwise, use the resolved row's inputs for trigger/inputs instantiation
            if isinstance(resolved_row.inputs, dict):
                resolved_inputs = resolved_row.inputs
            else:
                # Convert BaseInputs to dict
                resolved_inputs = {
                    desc.name: value for desc, value in resolved_row.inputs if not desc.name.startswith("__")
                }

        if trigger_id is None:
            inputs_class = cls.get_inputs_class()
            return inputs_class(**resolved_inputs)

        # Determine if trigger_id is a UUID or a name string
        resolved_trigger_id: Optional[UUID] = None
        trigger_name: Optional[str] = None

        if isinstance(trigger_id, UUID):
            resolved_trigger_id = trigger_id
        elif is_valid_uuid(trigger_id):
            resolved_trigger_id = UUID(trigger_id)
        else:
            trigger_name = trigger_id

        trigger_classes = []
        for subgraph in cls.get_subgraphs():
            for trigger_class in subgraph.triggers:
                # Match by UUID
                if resolved_trigger_id is not None and trigger_class.__id__ == resolved_trigger_id:
                    try:
                        return trigger_class(**resolved_inputs)
                    except Exception as e:
                        raise WorkflowInitializationException(
                            message=f"Failed to instantiate trigger {trigger_class.__name__}: {e}",
                            workflow_definition=cls,
                        ) from e

                # Match by name
                if trigger_name is not None and trigger_class.__trigger_name__ == trigger_name:
                    try:
                        return trigger_class(**resolved_inputs)
                    except Exception as e:
                        raise WorkflowInitializationException(
                            message=f"Failed to instantiate trigger {trigger_class.__name__}: {e}",
                            workflow_definition=cls,
                        ) from e

                trigger_classes.append(trigger_class)

        # Build helpful error message
        if trigger_name is not None:
            available_names = [trigger_class.__trigger_name__ for trigger_class in trigger_classes]
            raise WorkflowInitializationException(
                message=f"No trigger class found with name '{trigger_name}' in workflow {cls.__name__}. "
                f"Available trigger names: {available_names}"
            )
        else:
            raise WorkflowInitializationException(
                message=f"No trigger class found with id {trigger_id} in workflow {cls.__name__}. "
                f"Available trigger classes: {[trigger_class.__name__ for trigger_class in trigger_classes]}"
            )

    @staticmethod
    def load_from_module(module_path: str) -> Type["BaseWorkflow"]:
        workflow_path = f"{module_path}.workflow"
        try:
            module = importlib.import_module(workflow_path)
        except ValidationError as e:
            raise WorkflowInitializationException(
                message=f"Pydantic Model Validation defined in Workflow Failed: {e}"
            ) from e
        except TypeError as e:
            if "Unexpected graph type" in str(e) or "unhashable type: 'set'" in str(e):
                raise WorkflowInitializationException(
                    message="Invalid graph structure detected. Nested sets or unsupported graph types are not allowed. "
                    "Please contact Vellum support for assistance with Workflow configuration."
                ) from e
            else:
                raise WorkflowInitializationException(message=f"Type Error raised while loading Workflow: {e}") from e
        except SyntaxError as e:
            raise WorkflowInitializationException(message=f"Syntax Error raised while loading Workflow: {e}") from e
        except ModuleNotFoundError as e:
            error_message = f"Workflow module not found: {e}"
            raw_data: Optional[Dict[str, Any]] = None
            has_namespace_match = False
            for finder in sys.meta_path:
                if isinstance(finder, BaseWorkflowFinder):
                    error_message = finder.format_error_message(error_message)
                    if hasattr(finder, "namespace") and e.name and finder.namespace in e.name:
                        has_namespace_match = True
            if not has_namespace_match:
                raw_data = {"vellum_on_error_action": "CREATE_CUSTOM_IMAGE"}

            stacktrace = traceback.format_exc()
            tb = e.__traceback__
            if tb is not None:
                tb_entries = traceback.extract_tb(tb)
                if tb_entries:
                    last_entry = tb_entries[-1]
                    if raw_data is None:
                        raw_data = {}
                    raw_data["file"] = last_entry.filename
                    raw_data["lineno"] = last_entry.lineno

            raise WorkflowInitializationException(
                message=error_message, raw_data=raw_data, stacktrace=stacktrace
            ) from e
        except ImportError as e:
            raise WorkflowInitializationException(message=f"Invalid import found while loading Workflow: {e}") from e
        except NameError as e:
            raise WorkflowInitializationException(message=f"Invalid variable reference: {e}") from e
        except Exception as e:
            raise WorkflowInitializationException(message=f"Unexpected failure while loading module: {e}") from e

        # Attempt to load optional display sidecar module to trigger node ID annotations
        display_path = f"{module_path}.display"
        try:
            importlib.import_module(display_path)
        except ModuleNotFoundError:
            # No display package for this workflow; that's fine.
            pass
        except Exception as e:
            raise WorkflowInitializationException(
                message=f"Unexpected failure while loading display module '{display_path}': {e}"
            ) from e

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
            raise WorkflowInitializationException(f"No workflows found in {module_path}")
        elif len(workflows) > 1:
            raise WorkflowInitializationException(f"Multiple workflows found in {module_path}")
        return workflows[0]

    def join(self) -> None:
        """
        Wait for all emitters and runner to complete their background work.
        This ensures all pending events are processed before the workflow terminates.
        """
        if self._current_runner:
            self._current_runner.join()

        for emitter in self.emitters:
            emitter.join()

    @classmethod
    def _validate_no_self_edges(cls) -> None:
        """
        Validate that the workflow graph doesn't contain unconditional self-edges (infinite loops).

        A node is considered to have an unconditional self-edge if all of its ports target itself.

        Args:
            edges: List of edge dictionaries from the serialized workflow

        Raises:
            WorkflowInitializationException: If an unconditional self-edge is detected
        """

        for node in cls.get_all_nodes():
            node_ports = [list(port.edges) for port in node.Ports]
            if (
                all(
                    all(edge.to_node == node for edge in port_edges) and len(port_edges) > 0
                    for port_edges in node_ports
                )
                and len(node_ports) > 0
            ):
                raise WorkflowInitializationException(
                    message=f"Graph contains a self-edge ({node.__name__} >> {node.__name__}).",
                    workflow_definition=cls,
                    code=WorkflowErrorCode.INVALID_WORKFLOW,
                )


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
NodeExecutionLogBody.model_rebuild()

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
NodeExecutionLogEvent.model_rebuild()

StateMeta.model_rebuild()
