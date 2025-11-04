from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
import logging
from queue import Empty, Queue
import sys
from threading import Event as ThreadingEvent, Thread
import traceback
from uuid import UUID, uuid4
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from vellum.workflows.constants import undefined
from vellum.workflows.context import ExecutionContext, execution_context, get_execution_context
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.errors import WorkflowError, WorkflowErrorCode
from vellum.workflows.events import (
    NodeExecutionFulfilledEvent,
    NodeExecutionInitiatedEvent,
    NodeExecutionRejectedEvent,
    NodeExecutionStreamingEvent,
    WorkflowEvent,
    WorkflowEventGenerator,
    WorkflowExecutionFulfilledEvent,
    WorkflowExecutionInitiatedEvent,
    WorkflowExecutionRejectedEvent,
    WorkflowExecutionStreamingEvent,
)
from vellum.workflows.events.node import (
    NodeEvent,
    NodeExecutionFulfilledBody,
    NodeExecutionInitiatedBody,
    NodeExecutionRejectedBody,
    NodeExecutionStreamingBody,
)
from vellum.workflows.events.types import BaseEvent, NodeParentContext, ParentContext, SpanLink, WorkflowParentContext
from vellum.workflows.events.workflow import (
    WorkflowEventStream,
    WorkflowExecutionFulfilledBody,
    WorkflowExecutionInitiatedBody,
    WorkflowExecutionPausedBody,
    WorkflowExecutionPausedEvent,
    WorkflowExecutionRejectedBody,
    WorkflowExecutionResumedBody,
    WorkflowExecutionResumedEvent,
    WorkflowExecutionSnapshottedBody,
    WorkflowExecutionSnapshottedEvent,
    WorkflowExecutionStreamingBody,
)
from vellum.workflows.exceptions import NodeException, WorkflowInitializationException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.bases.base import NodeRunResponse
from vellum.workflows.nodes.mocks import MockNodeExecutionArg
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.ports.port import Port
from vellum.workflows.references import ExternalInputReference, OutputReference
from vellum.workflows.references.state_value import StateValueReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.delta import StateDelta
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.types.core import CancelSignal
from vellum.workflows.types.generics import InputsType, OutputsType, StateType

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow

logger = logging.getLogger(__name__)

RunFromNodeArg = Sequence[Union[Type[BaseNode], UUID]]
ExternalInputsArg = Dict[ExternalInputReference, Any]
BackgroundThreadItem = Union[BaseState, WorkflowEvent, None]


@dataclass
class ActiveNode(Generic[StateType]):
    node: BaseNode[StateType]
    was_outputs_streamed: bool = False


class WorkflowRunner(Generic[StateType]):
    _entrypoints: Iterable[Type[BaseNode]]

    def __init__(
        self,
        workflow: "BaseWorkflow[InputsType, StateType]",
        inputs: Optional[InputsType] = None,
        state: Optional[StateType] = None,
        entrypoint_nodes: Optional[RunFromNodeArg] = None,
        external_inputs: Optional[ExternalInputsArg] = None,
        previous_execution_id: Optional[Union[str, UUID]] = None,
        cancel_signal: Optional[CancelSignal] = None,
        node_output_mocks: Optional[MockNodeExecutionArg] = None,
        max_concurrency: Optional[int] = None,
        timeout: Optional[float] = None,
        init_execution_context: Optional[ExecutionContext] = None,
        trigger: Optional[BaseTrigger] = None,
        execution_id: Optional[UUID] = None,
    ):
        if state and external_inputs:
            raise ValueError("Can only run a Workflow providing one of state or external inputs, not both")

        self.workflow = workflow
        self._is_resuming = False
        self._should_emit_initial_state = True
        self._span_link_info: Optional[Tuple[str, str, str, str]] = None
        if entrypoint_nodes:
            nodes_by_id = {node.__id__: node for node in self.workflow.get_all_nodes()}

            resolved_nodes = []
            for item in entrypoint_nodes:
                if isinstance(item, UUID):
                    matching_node = nodes_by_id.get(item)
                    if matching_node is None:
                        raise ValueError(f"No node found with UUID {item}")
                    resolved_nodes.append(matching_node)
                else:
                    resolved_nodes.append(item)

            if len(list(resolved_nodes)) > 1:
                raise WorkflowInitializationException("Cannot resume from multiple nodes")

            # TODO: Support resuming from multiple nodes
            # https://app.shortcut.com/vellum/story/4408
            node = next(iter(resolved_nodes))
            if state:
                self._initial_state = deepcopy(state)
                self._initial_state.meta.span_id = execution_id or uuid4()
                self._initial_state.meta.workflow_definition = self.workflow.__class__
            else:
                self._initial_state = self.workflow.get_state_at_node(node)
            self._entrypoints = resolved_nodes
        elif external_inputs:
            self._initial_state = self.workflow.get_most_recent_state(execution_id)
            for descriptor, value in external_inputs.items():
                if not any(isinstance(value, type_) for type_ in descriptor.types):
                    raise NodeException(
                        f"Invalid external input type for {descriptor.name}",
                        code=WorkflowErrorCode.INVALID_INPUTS,
                    )
                self._initial_state.meta.external_inputs[descriptor] = value

            self._entrypoints = [
                ei.inputs_class.__parent_class__
                for ei in external_inputs
                if issubclass(ei.inputs_class.__parent_class__, BaseNode)
            ]
            self._is_resuming = True
        elif previous_execution_id:
            if not self.workflow.resolvers:
                raise WorkflowInitializationException(
                    message=f"No resolvers configured to load initial state for execution ID: {previous_execution_id}",
                    workflow_definition=self.workflow.__class__,
                    code=WorkflowErrorCode.INVALID_INPUTS,
                )

            resolver_failed = True
            for resolver in self.workflow.resolvers:
                try:
                    load_state_result = resolver.load_state(previous_execution_id)

                    if load_state_result is not None:
                        if execution_id:
                            load_state_result.state.meta.span_id = execution_id

                        state_class = self.workflow.get_state_class()
                        if isinstance(load_state_result.state, state_class):
                            self._initial_state = load_state_result.state
                            normalized_inputs = deepcopy(inputs) if inputs else self.workflow.get_default_inputs()
                            self._initial_state.meta.workflow_inputs = normalized_inputs
                            self._initial_state.meta.workflow_definition = self.workflow.__class__
                            self._span_link_info = (
                                load_state_result.previous_trace_id,
                                load_state_result.previous_span_id,
                                load_state_result.root_trace_id,
                                load_state_result.root_span_id,
                            )
                            resolver_failed = False
                            break
                except Exception as e:
                    logger.warning(f"Failed to load state from resolver {type(resolver).__name__}: {e}")
                    continue

            if resolver_failed:
                raise WorkflowInitializationException(
                    message=f"All resolvers failed to load initial state for execution ID: {previous_execution_id}",
                    workflow_definition=self.workflow.__class__,
                    code=WorkflowErrorCode.INVALID_INPUTS,
                )

            self._entrypoints = self.workflow.get_entrypoints()
        elif trigger:
            # When trigger is provided, set up default state and filter entrypoints by trigger type
            normalized_inputs = deepcopy(inputs) if inputs else self.workflow.get_default_inputs()
            if state:
                self._initial_state = deepcopy(state)
                self._initial_state.meta.workflow_inputs = normalized_inputs
                self._initial_state.meta.span_id = execution_id or uuid4()
                self._initial_state.meta.workflow_definition = self.workflow.__class__
            else:
                self._initial_state = self.workflow.get_default_state(normalized_inputs, execution_id)
                self._should_emit_initial_state = False

            # Validate and bind trigger, then filter entrypoints
            self._validate_and_bind_trigger(trigger)
            self._entrypoints = self.workflow.get_entrypoints()
            self._filter_entrypoints_for_trigger(trigger)
        else:
            # Default case: no entrypoint overrides and no trigger
            normalized_inputs = deepcopy(inputs) if inputs else self.workflow.get_default_inputs()
            if state:
                self._initial_state = deepcopy(state)
                self._initial_state.meta.workflow_inputs = normalized_inputs
                self._initial_state.meta.span_id = execution_id or uuid4()
                self._initial_state.meta.workflow_definition = self.workflow.__class__
            else:
                self._initial_state = self.workflow.get_default_state(normalized_inputs, execution_id)
                # We don't want to emit the initial state on the base case of Workflow Runs, since
                # all of that data is redundant and is derivable. It also clearly communicates that
                # there was no initial state provided by the user to invoke the workflow.
                self._should_emit_initial_state = False
            self._entrypoints = self.workflow.get_entrypoints()

            # Check if workflow requires a trigger but none was provided
            self._validate_no_trigger_provided()

        # This queue is responsible for sending events from WorkflowRunner to the outside world
        self._workflow_event_outer_queue: Queue[WorkflowEvent] = Queue()

        # This queue is responsible for sending events from the inner worker threads to WorkflowRunner
        self._workflow_event_inner_queue: Queue[WorkflowEvent] = Queue()

        self._max_concurrency = max_concurrency
        self._concurrency_queue: Queue[Tuple[StateType, Type[BaseNode], Optional[UUID]]] = Queue()

        # This queue is responsible for sending events from WorkflowRunner to the background thread
        # for user defined emitters
        self._background_thread_queue: Queue[BackgroundThreadItem] = Queue()

        self._dependencies: Dict[Type[BaseNode], Set[Type[BaseNode]]] = defaultdict(set)
        self._state_forks: Set[StateType] = {self._initial_state}

        self._active_nodes_by_execution_id: Dict[UUID, ActiveNode[StateType]] = {}
        self._cancel_signal = cancel_signal
        self._timeout = timeout
        self._execution_context = init_execution_context or get_execution_context()

        setattr(
            self._initial_state,
            "__snapshot_callback__",
            lambda s, d: self._snapshot_state(s, d),
        )
        self.workflow.context._register_event_queue(self._workflow_event_inner_queue)
        self.workflow.context._register_node_output_mocks(node_output_mocks or [])

        self._outputs_listening_to_state = [
            descriptor for descriptor in self.workflow.Outputs if isinstance(descriptor.instance, StateValueReference)
        ]

        self._background_thread: Optional[Thread] = None
        self._cancel_thread: Optional[Thread] = None
        self._timeout_thread: Optional[Thread] = None

    def _has_manual_trigger(self) -> bool:
        """Check if workflow has ManualTrigger."""
        for subgraph in self.workflow.get_subgraphs():
            for trigger in subgraph.triggers:
                if issubclass(trigger, ManualTrigger):
                    return True
        return False

    def _get_entrypoints_for_trigger_type(self, trigger_class: Type) -> List[Type[BaseNode]]:
        """Get all entrypoints connected to a specific trigger type.

        Allows subclasses: if trigger_class is a subclass of any declared trigger,
        returns those entrypoints.
        """
        entrypoints: List[Type[BaseNode]] = []
        for subgraph in self.workflow.get_subgraphs():
            for trigger in subgraph.triggers:
                # Check if the provided trigger_class is a subclass of the declared trigger
                # This allows runtime instances to be subclasses of what's declared in the workflow
                if issubclass(trigger_class, trigger):
                    entrypoints.extend(subgraph.entrypoints)
        return entrypoints

    def _validate_and_bind_trigger(self, trigger: BaseTrigger) -> None:
        """
        Validate that trigger is compatible with workflow and bind it to state.

        Supports all trigger types derived from BaseTrigger:
        - IntegrationTrigger instances (Slack, Gmail, etc.)
        - ManualTrigger instances (explicit manual execution)
        - ScheduledTrigger instances (time-based triggers)
        - Any future trigger types

        Raises:
            WorkflowInitializationException: If trigger type is not compatible with workflow
        """
        trigger_class = type(trigger)

        # Search for a compatible trigger type in the workflow
        found_compatible_trigger = False
        has_any_triggers = False
        incompatible_trigger_names: List[str] = []

        for subgraph in self.workflow.get_subgraphs():
            for declared_trigger in subgraph.triggers:
                has_any_triggers = True
                # Allow subclasses: if workflow declares BaseSlackTrigger, accept SpecificSlackTrigger instances
                if issubclass(trigger_class, declared_trigger):
                    found_compatible_trigger = True
                    break
                else:
                    incompatible_trigger_names.append(declared_trigger.__name__)

            if found_compatible_trigger:
                break

        # Special case: workflows with no explicit triggers implicitly support ManualTrigger
        if not has_any_triggers and not isinstance(trigger, ManualTrigger):
            raise WorkflowInitializationException(
                message=f"Provided trigger type {trigger_class.__name__} is not compatible with workflow. "
                f"Workflow has no explicit triggers and only supports ManualTrigger.",
                workflow_definition=self.workflow.__class__,
                code=WorkflowErrorCode.INVALID_INPUTS,
            )

        # Validate that we found a compatible trigger type
        if has_any_triggers and not found_compatible_trigger:
            raise WorkflowInitializationException(
                message=f"Provided trigger type {trigger_class.__name__} is not compatible with workflow triggers. "
                f"Workflow has: {sorted(set(incompatible_trigger_names))}",
                workflow_definition=self.workflow.__class__,
                code=WorkflowErrorCode.INVALID_INPUTS,
            )

        # Bind trigger to state (works for all trigger types via BaseTrigger.bind_to_state)
        trigger.bind_to_state(self._initial_state)

    def _filter_entrypoints_for_trigger(self, trigger: BaseTrigger) -> None:
        """
        Filter entrypoints to those connected to the specific trigger type.

        Uses the specific trigger subclass, not the parent class, allowing workflows
        with multiple triggers to route to the correct path.
        """
        trigger_class = type(trigger)
        specific_entrypoints = self._get_entrypoints_for_trigger_type(trigger_class)
        if specific_entrypoints:
            self._entrypoints = specific_entrypoints

    def _validate_no_trigger_provided(self) -> None:
        """
        Validate that workflow can run without a trigger.

        If workflow has IntegrationTrigger(s) but no ManualTrigger, it requires a trigger instance.
        If workflow has both, filter entrypoints to ManualTrigger path only.

        Raises:
            WorkflowInitializationException: If workflow requires trigger but none was provided
        """
        # Collect all IntegrationTrigger types in the workflow
        workflow_integration_triggers = []
        for subgraph in self.workflow.get_subgraphs():
            for trigger_type in subgraph.triggers:
                if issubclass(trigger_type, IntegrationTrigger):
                    workflow_integration_triggers.append(trigger_type)

        if workflow_integration_triggers:
            if not self._has_manual_trigger():
                # Workflow has ONLY IntegrationTrigger - this is an error
                raise WorkflowInitializationException(
                    message="Workflow has IntegrationTrigger which requires trigger parameter",
                    workflow_definition=self.workflow.__class__,
                    code=WorkflowErrorCode.INVALID_INPUTS,
                )

            # Workflow has both IntegrationTrigger and ManualTrigger - filter to ManualTrigger path
            manual_entrypoints = self._get_entrypoints_for_trigger_type(ManualTrigger)
            if manual_entrypoints:
                self._entrypoints = manual_entrypoints

    @contextmanager
    def _httpx_logger_with_span_id(self) -> Iterator[None]:
        """
        Context manager to append the current execution's span ID to httpx logger messages.

        This is used when making API requests via the Vellum client to include
        the execution's span ID in the httpx request logs for better traceability.
        """
        httpx_logger = logging.getLogger("httpx")

        class SpanIdFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                if record.name == "httpx" and "[span_id=" not in record.msg:
                    context = get_execution_context()
                    if context.parent_context:
                        span_id = str(context.parent_context.span_id)
                        record.msg = f"{record.msg} [span_id={span_id}]"
                return True

        span_filter = SpanIdFilter()
        httpx_logger.addFilter(span_filter)

        try:
            yield
        finally:
            httpx_logger.removeFilter(span_filter)

    def _snapshot_state(self, state: StateType, deltas: List[StateDelta]) -> StateType:
        execution = get_execution_context()
        edited_by = None
        if execution.parent_context and hasattr(execution.parent_context, "node_definition"):
            edited_by = execution.parent_context.node_definition

        self._workflow_event_inner_queue.put(
            WorkflowExecutionSnapshottedEvent(
                trace_id=self._execution_context.trace_id,
                span_id=state.meta.span_id,
                body=WorkflowExecutionSnapshottedBody(
                    workflow_definition=self.workflow.__class__,
                    state=state,
                    edited_by=edited_by,
                ),
                parent=self._execution_context.parent_context,
            )
        )

        delta_names = [d.name for d in deltas]
        for descriptor in self._outputs_listening_to_state:
            if not isinstance(descriptor.instance, StateValueReference):
                continue

            if descriptor.instance.name not in delta_names:
                continue

            resolved_delta = descriptor.instance.resolve(state)
            if resolved_delta is undefined:
                continue

            self._workflow_event_outer_queue.put(
                self._stream_workflow_event(
                    BaseOutput(
                        name=descriptor.name,
                        # We may want to switch this to using the delta from the state delta
                        # instead of the state value. In the short term, we need to show
                        # the full conversation of the tool calling node's delta's.
                        delta=resolved_delta,
                    )
                )
            )

        self.workflow._store.append_state_snapshot(state)
        self._background_thread_queue.put(state)
        return state

    def _emit_event(self, event: WorkflowEvent) -> WorkflowEvent:
        self.workflow._store.append_event(event)
        self._background_thread_queue.put(event)
        return event

    def _run_work_item(self, node: BaseNode[StateType], span_id: UUID) -> None:
        for event in self.run_node(node, span_id):
            self._workflow_event_inner_queue.put(event)

    def run_node(
        self,
        node: "BaseNode[StateType]",
        span_id: UUID,
    ) -> Generator[NodeEvent, None, None]:
        """
        Execute a single node and yield workflow events.

        Args:
            node: The node instance to execute
            span_id: Unique identifier for this node execution

        Yields:
            NodeExecutionEvent: Events emitted during node execution (initiated, streaming, fulfilled, rejected)
        """
        execution = get_execution_context()

        node_output_mocks_map = self.workflow.context.node_output_mocks_map

        yield NodeExecutionInitiatedEvent(
            trace_id=execution.trace_id,
            span_id=span_id,
            body=NodeExecutionInitiatedBody(
                node_definition=node.__class__,
                inputs=node._inputs,
            ),
            parent=execution.parent_context,
        )

        logger.debug(f"Started running node: {node.__class__.__name__}")

        try:
            updated_parent_context = NodeParentContext(
                span_id=span_id,
                node_definition=node.__class__,
                parent=execution.parent_context,
            )
            node_run_response: NodeRunResponse
            was_mocked: Optional[bool] = None
            mock_candidates = node_output_mocks_map.get(node.Outputs) or []
            for mock_candidate in mock_candidates:
                if mock_candidate.when_condition.resolve(node.state):
                    node_run_response = mock_candidate.then_outputs
                    was_mocked = True
                    break

            if not was_mocked:
                with execution_context(parent_context=updated_parent_context, trace_id=execution.trace_id):
                    node_run_response = node.run()

            ports = node.Ports()
            if not isinstance(node_run_response, (BaseOutputs, Iterator)):
                raise NodeException(
                    message=f"Node {node.__class__.__name__} did not return a valid node run response",
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                )

            if isinstance(node_run_response, BaseOutputs):
                if not isinstance(node_run_response, node.Outputs):
                    raise NodeException(
                        message=f"Node {node.__class__.__name__} did not return a valid outputs object",
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                    )

                outputs = node_run_response
            else:
                streaming_output_queues: Dict[str, Queue] = {}
                outputs = node.Outputs()

                def initiate_node_streaming_output(
                    output: BaseOutput,
                ) -> Generator[NodeExecutionStreamingEvent, None, None]:
                    streaming_output_queues[output.name] = Queue()
                    output_descriptor = OutputReference(
                        name=output.name,
                        types=(type(output.delta),),
                        instance=None,
                        outputs_class=node.Outputs,
                    )
                    with node.state.__quiet__():
                        node.state.meta.node_outputs[output_descriptor] = streaming_output_queues[output.name]
                    initiated_output: BaseOutput = BaseOutput(name=output.name)
                    initiated_ports = initiated_output > ports
                    yield NodeExecutionStreamingEvent(
                        trace_id=execution.trace_id,
                        span_id=span_id,
                        body=NodeExecutionStreamingBody(
                            node_definition=node.__class__,
                            output=initiated_output,
                            invoked_ports=initiated_ports,
                        ),
                        parent=execution.parent_context,
                    )

                with execution_context(parent_context=updated_parent_context, trace_id=execution.trace_id):
                    for output in node_run_response:
                        invoked_ports = output > ports
                        if output.is_initiated:
                            yield from initiate_node_streaming_output(output)
                        elif output.is_streaming:
                            if output.name not in streaming_output_queues:
                                yield from initiate_node_streaming_output(output)

                            streaming_output_queues[output.name].put(output.delta)
                            yield NodeExecutionStreamingEvent(
                                trace_id=execution.trace_id,
                                span_id=span_id,
                                body=NodeExecutionStreamingBody(
                                    node_definition=node.__class__,
                                    output=output,
                                    invoked_ports=invoked_ports,
                                ),
                                parent=execution.parent_context,
                            )
                        elif output.is_fulfilled:
                            if output.name in streaming_output_queues:
                                streaming_output_queues[output.name].put(undefined)

                            setattr(outputs, output.name, output.value)
                            yield NodeExecutionStreamingEvent(
                                trace_id=execution.trace_id,
                                span_id=span_id,
                                body=NodeExecutionStreamingBody(
                                    node_definition=node.__class__,
                                    output=output,
                                    invoked_ports=invoked_ports,
                                ),
                                parent=execution.parent_context,
                            )

            node.state.meta.node_execution_cache.fulfill_node_execution(node.__class__, span_id)

            with execution_context(parent_context=updated_parent_context, trace_id=execution.trace_id):
                with node.state.__atomic__():
                    for descriptor, output_value in outputs:
                        if output_value is undefined:
                            if descriptor in node.state.meta.node_outputs:
                                del node.state.meta.node_outputs[descriptor]
                            continue
                        node.state.meta.node_outputs[descriptor] = output_value

            invoked_ports = ports(outputs, node.state)
            yield NodeExecutionFulfilledEvent(
                trace_id=execution.trace_id,
                span_id=span_id,
                body=NodeExecutionFulfilledBody(
                    node_definition=node.__class__,
                    outputs=outputs,
                    invoked_ports=invoked_ports,
                    mocked=was_mocked,
                ),
                parent=execution.parent_context,
            )
        except NodeException as e:
            yield self._handle_run_node_exception(e, "Node Exception", execution, span_id, node)
        except WorkflowInitializationException as e:
            yield self._handle_run_node_exception(e, "Workflow Initialization Exception", execution, span_id, node)
        except InvalidExpressionException as e:
            yield self._handle_run_node_exception(e, "Invalid Expression Exception", execution, span_id, node)
        except Exception as e:
            error_message = self._parse_error_message(e)
            captured_stacktrace = traceback.format_exc()
            if error_message is None:
                logger.exception(f"An unexpected error occurred while running node {node.__class__.__name__}")
                error_code = WorkflowErrorCode.INTERNAL_ERROR
                error_message = "Internal error"
            else:
                error_code = WorkflowErrorCode.NODE_EXECUTION

            yield NodeExecutionRejectedEvent(
                trace_id=execution.trace_id,
                span_id=span_id,
                body=NodeExecutionRejectedBody(
                    node_definition=node.__class__,
                    error=WorkflowError(
                        message=error_message,
                        code=error_code,
                    ),
                    stacktrace=captured_stacktrace,
                ),
                parent=execution.parent_context,
            )

        logger.debug(f"Finished running node: {node.__class__.__name__}")

    def _handle_run_node_exception(
        self,
        exception: Union[NodeException, WorkflowInitializationException, InvalidExpressionException],
        prefix: str,
        execution: ExecutionContext,
        span_id: UUID,
        node: BaseNode[StateType],
    ) -> NodeExecutionRejectedEvent:
        logger.info(f"{prefix}: {exception}")
        captured_stacktrace = traceback.format_exc()

        return NodeExecutionRejectedEvent(
            trace_id=execution.trace_id,
            span_id=span_id,
            body=NodeExecutionRejectedBody(
                node_definition=node.__class__,
                error=exception.error,
                stacktrace=captured_stacktrace,
            ),
            parent=execution.parent_context,
        )

    def _parse_error_message(self, exception: Exception) -> Optional[str]:
        try:
            _, _, tb = sys.exc_info()
            if tb:
                tb_list = traceback.extract_tb(tb)
                if tb_list:
                    for frame in reversed(tb_list):
                        exception_module = next(
                            (
                                mod.__name__
                                for mod in sys.modules.values()
                                if hasattr(mod, "__file__") and mod.__file__ == frame.filename
                            ),
                            None,
                        )
                        if exception_module and not exception_module.startswith("vellum."):
                            return str(exception)
        except Exception:
            pass

        return None

    def _context_run_work_item(
        self,
        node: BaseNode[StateType],
        span_id: UUID,
        parent_context: ParentContext,
        trace_id: UUID,
    ) -> None:
        with execution_context(
            parent_context=parent_context,
            trace_id=trace_id,
        ):
            self._run_work_item(node, span_id)

    def _handle_invoked_ports(
        self,
        state: StateType,
        ports: Optional[Iterable[Port]],
        invoked_by: Optional[UUID],
    ) -> None:
        if not ports:
            return

        for port in ports:
            for edge in port.edges:
                if port.fork_state:
                    next_state = deepcopy(state)
                    self._state_forks.add(next_state)
                else:
                    next_state = state

                if self._max_concurrency:
                    self._concurrency_queue.put((next_state, edge.to_node, invoked_by))
                else:
                    self._run_node_if_ready(next_state, edge.to_node, invoked_by)

        if self._max_concurrency:
            num_nodes_to_run = self._max_concurrency - len(self._active_nodes_by_execution_id)
            for _ in range(num_nodes_to_run):
                if self._concurrency_queue.empty():
                    break

                next_state, node_class, invoked_by = self._concurrency_queue.get()
                self._run_node_if_ready(next_state, node_class, invoked_by)

    def _run_node_if_ready(
        self,
        state: StateType,
        node_class: Type[BaseNode],
        invoked_by: Optional[UUID] = None,
    ) -> None:
        with state.__lock__:
            for descriptor in node_class.ExternalInputs:
                if not isinstance(descriptor, ExternalInputReference):
                    continue

                if state.meta.external_inputs.get(descriptor, undefined) is undefined:
                    state.meta.external_inputs[descriptor] = undefined
                    return

            all_deps = self._dependencies[node_class]
            node_span_id = node_class.Trigger._queue_node_execution(state, all_deps, invoked_by)

            try:
                if not node_class.Trigger.should_initiate(state, all_deps, node_span_id):
                    return
            except NodeException as e:
                execution = get_execution_context()

                self._workflow_event_outer_queue.put(
                    WorkflowExecutionRejectedEvent(
                        trace_id=execution.trace_id,
                        span_id=node_span_id,
                        body=WorkflowExecutionRejectedBody(
                            workflow_definition=self.workflow.__class__,
                            error=e.error,
                        ),
                    )
                )
                raise e

            execution = get_execution_context()
            node = node_class(state=state, context=self.workflow.context)
            state.meta.node_execution_cache.initiate_node_execution(node_class, node_span_id)
            self._active_nodes_by_execution_id[node_span_id] = ActiveNode(node=node)

            worker_thread = Thread(
                target=self._context_run_work_item,
                kwargs={
                    "node": node,
                    "span_id": node_span_id,
                    "parent_context": execution.parent_context,
                    "trace_id": execution.trace_id,
                },
            )
            worker_thread.start()

    def _handle_work_item_event(self, event: WorkflowEvent) -> Optional[NodeExecutionRejectedEvent]:
        active_node = self._active_nodes_by_execution_id.get(event.span_id)
        if not active_node:
            return None

        node = active_node.node
        if event.name == "node.execution.rejected":
            self._active_nodes_by_execution_id.pop(event.span_id)
            return event

        if event.name == "node.execution.streaming":
            for workflow_output_descriptor in self.workflow.Outputs:
                if node.__directly_emit_workflow_output__(event, workflow_output_descriptor):
                    active_node.was_outputs_streamed = True
                    self._workflow_event_outer_queue.put(
                        self._stream_workflow_event(
                            BaseOutput(
                                name=workflow_output_descriptor.name,
                                value=event.output.value,
                                delta=event.output.delta,
                            )
                        )
                    )
                    return None

                node_output_descriptor = workflow_output_descriptor.instance
                if not isinstance(node_output_descriptor, OutputReference):
                    continue
                if node_output_descriptor.outputs_class != event.node_definition.Outputs:
                    continue
                if node_output_descriptor.name != event.output.name:
                    continue

                active_node.was_outputs_streamed = True
                self._workflow_event_outer_queue.put(
                    self._stream_workflow_event(
                        BaseOutput(
                            name=workflow_output_descriptor.name,
                            value=event.output.value,
                            delta=event.output.delta,
                        )
                    )
                )

            self._handle_invoked_ports(node.state, event.invoked_ports, event.span_id)

            return None

        if event.name == "node.execution.fulfilled":
            self._active_nodes_by_execution_id.pop(event.span_id)
            if not active_node.was_outputs_streamed:
                for event_node_output_descriptor, node_output_value in event.outputs:
                    for workflow_output_descriptor in self.workflow.Outputs:
                        node_output_descriptor = workflow_output_descriptor.instance
                        if not isinstance(node_output_descriptor, OutputReference):
                            continue
                        if node_output_descriptor.outputs_class != event.node_definition.Outputs:
                            continue
                        if node_output_descriptor.name != event_node_output_descriptor.name:
                            continue

                        self._workflow_event_outer_queue.put(
                            self._stream_workflow_event(
                                BaseOutput(
                                    name=workflow_output_descriptor.name,
                                    value=node_output_value,
                                )
                            )
                        )

            self._handle_invoked_ports(node.state, event.invoked_ports, event.span_id)

            return None

        return None

    def _emit_node_cancellation_events(
        self,
        error_message: str,
    ) -> None:
        """
        Emit node cancellation events for all active nodes.

        Args:
            error_message: The error message to include in the cancellation events
        """
        parent_context = WorkflowParentContext(
            span_id=self._initial_state.meta.span_id,
            workflow_definition=self.workflow.__class__,
            parent=self._execution_context.parent_context,
        )
        captured_stacktrace = "".join(traceback.format_stack())
        active_span_ids = list(self._active_nodes_by_execution_id.keys())
        for span_id in active_span_ids:
            active_node = self._active_nodes_by_execution_id.pop(span_id, None)
            if active_node is not None:
                rejection_event = NodeExecutionRejectedEvent(
                    trace_id=self._execution_context.trace_id,
                    span_id=span_id,
                    body=NodeExecutionRejectedBody(
                        node_definition=active_node.node.__class__,
                        error=WorkflowError(
                            code=WorkflowErrorCode.NODE_CANCELLED,
                            message=error_message,
                        ),
                        stacktrace=captured_stacktrace,
                    ),
                    parent=parent_context,
                )
                self._workflow_event_outer_queue.put(rejection_event)

    def _initiate_workflow_event(self) -> WorkflowExecutionInitiatedEvent:
        links: Optional[List[SpanLink]] = None

        if self._span_link_info:
            previous_trace_id, previous_span_id, root_trace_id, root_span_id = self._span_link_info
            links = [
                SpanLink(
                    trace_id=previous_trace_id,
                    type="PREVIOUS_SPAN",
                    span_context=WorkflowParentContext(
                        workflow_definition=self.workflow.__class__,
                        span_id=previous_span_id,
                    ),
                ),
                SpanLink(
                    trace_id=root_trace_id,
                    type="ROOT_SPAN",
                    span_context=WorkflowParentContext(
                        workflow_definition=self.workflow.__class__,
                        span_id=root_span_id,
                    ),
                ),
            ]

        return WorkflowExecutionInitiatedEvent(
            trace_id=self._execution_context.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionInitiatedBody(
                workflow_definition=self.workflow.__class__,
                inputs=self._initial_state.meta.workflow_inputs,
                initial_state=deepcopy(self._initial_state) if self._should_emit_initial_state else None,
            ),
            parent=self._execution_context.parent_context,
            links=links,
        )

    def _stream_workflow_event(self, output: BaseOutput) -> WorkflowExecutionStreamingEvent:
        return WorkflowExecutionStreamingEvent(
            trace_id=self._execution_context.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionStreamingBody(
                workflow_definition=self.workflow.__class__,
                output=output,
            ),
            parent=self._execution_context.parent_context,
        )

    def _fulfill_workflow_event(self, outputs: OutputsType, final_state: StateType) -> WorkflowExecutionFulfilledEvent:
        return WorkflowExecutionFulfilledEvent(
            trace_id=self._execution_context.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionFulfilledBody(
                workflow_definition=self.workflow.__class__,
                outputs=outputs,
                final_state=final_state,
            ),
            parent=self._execution_context.parent_context,
        )

    def _reject_workflow_event(
        self, error: WorkflowError, captured_stacktrace: Optional[str] = None
    ) -> WorkflowExecutionRejectedEvent:
        if captured_stacktrace is None:
            try:
                captured_stacktrace = traceback.format_exc()
                if captured_stacktrace.strip() == "NoneType: None":
                    captured_stacktrace = None
            except Exception:
                pass

        return WorkflowExecutionRejectedEvent(
            trace_id=self._execution_context.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionRejectedBody(
                workflow_definition=self.workflow.__class__,
                error=error,
                stacktrace=captured_stacktrace,
            ),
            parent=self._execution_context.parent_context,
        )

    def _resume_workflow_event(self) -> WorkflowExecutionResumedEvent:
        return WorkflowExecutionResumedEvent(
            trace_id=self._execution_context.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionResumedBody(
                workflow_definition=self.workflow.__class__,
            ),
            parent=self._execution_context.parent_context,
        )

    def _pause_workflow_event(self, external_inputs: Iterable[ExternalInputReference]) -> WorkflowExecutionPausedEvent:
        return WorkflowExecutionPausedEvent(
            trace_id=self._execution_context.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionPausedBody(
                workflow_definition=self.workflow.__class__,
                external_inputs=external_inputs,
            ),
            parent=self._execution_context.parent_context,
        )

    def _wrapped_stream(self) -> None:
        """Wrapper for _stream that adds httpx logger span ID context."""
        with self._httpx_logger_with_span_id():
            self._stream()

    def _stream(self) -> None:
        for edge in self.workflow.get_edges():
            self._dependencies[edge.to_node].add(edge.from_port.node_class)

        current_parent = WorkflowParentContext(
            span_id=self._initial_state.meta.span_id,
            workflow_definition=self.workflow.__class__,
            parent=self._execution_context.parent_context,
            type="WORKFLOW",
        )
        for node_cls in self._entrypoints:
            try:
                if not self._max_concurrency or len(self._active_nodes_by_execution_id) < self._max_concurrency:
                    with execution_context(parent_context=current_parent, trace_id=self._execution_context.trace_id):
                        self._run_node_if_ready(self._initial_state, node_cls)
                else:
                    self._concurrency_queue.put((self._initial_state, node_cls, None))
            except NodeException as e:
                captured_stacktrace = traceback.format_exc()
                self._workflow_event_outer_queue.put(self._reject_workflow_event(e.error, captured_stacktrace))
                return
            except WorkflowInitializationException as e:
                captured_stacktrace = traceback.format_exc()
                self._workflow_event_outer_queue.put(self._reject_workflow_event(e.error, captured_stacktrace))
                return
            except Exception:
                err_message = f"An unexpected error occurred while initializing node {node_cls.__name__}"
                logger.exception(err_message)
                captured_stacktrace = traceback.format_exc()
                self._workflow_event_outer_queue.put(
                    self._reject_workflow_event(
                        WorkflowError(code=WorkflowErrorCode.INTERNAL_ERROR, message=err_message),
                        captured_stacktrace,
                    )
                )
                return

        rejection_event: Optional[NodeExecutionRejectedEvent] = None

        while True:
            if not self._active_nodes_by_execution_id:
                break

            event = self._workflow_event_inner_queue.get()

            self._workflow_event_outer_queue.put(event)

            with execution_context(parent_context=current_parent, trace_id=self._execution_context.trace_id):
                rejection_event = self._handle_work_item_event(event)

            if rejection_event:
                failed_node_name = rejection_event.body.node_definition.__name__
                self._emit_node_cancellation_events(
                    error_message=f"Node execution cancelled due to {failed_node_name} failure",
                )
                break

        # Handle any remaining events
        try:
            while event := self._workflow_event_inner_queue.get_nowait():
                self._workflow_event_outer_queue.put(event)

                with execution_context(parent_context=current_parent, trace_id=self._execution_context.trace_id):
                    rejection_event = self._handle_work_item_event(event)

                if rejection_event:
                    break
        except Empty:
            pass

        final_state = self._state_forks.pop()
        for other_state in self._state_forks:
            final_state += other_state

        unresolved_external_inputs = {
            descriptor
            for descriptor, node_input_value in final_state.meta.external_inputs.items()
            if node_input_value is undefined
        }
        if unresolved_external_inputs:
            self._workflow_event_outer_queue.put(
                self._pause_workflow_event(unresolved_external_inputs),
            )
            return

        if rejection_event:
            self._workflow_event_outer_queue.put(
                self._reject_workflow_event(rejection_event.error, rejection_event.body.stacktrace)
            )
            return

        fulfilled_outputs = self.workflow.Outputs()
        for descriptor, value in fulfilled_outputs:
            if isinstance(value, BaseDescriptor):
                setattr(fulfilled_outputs, descriptor.name, value.resolve(final_state))
            elif isinstance(descriptor.instance, BaseDescriptor):
                setattr(
                    fulfilled_outputs,
                    descriptor.name,
                    descriptor.instance.resolve(final_state),
                )

        self._workflow_event_outer_queue.put(self._fulfill_workflow_event(fulfilled_outputs, final_state))

    def _run_background_thread(self) -> None:
        state_class = self.workflow.get_state_class()
        while True:
            item = self._background_thread_queue.get()
            if item is None:
                break

            if isinstance(item, state_class):
                for emitter in self.workflow.emitters:
                    emitter.snapshot_state(item)
            elif isinstance(item, BaseEvent):
                for emitter in self.workflow.emitters:
                    emitter.emit_event(item)

    def _run_cancel_thread(self, kill_switch: ThreadingEvent) -> None:
        if not self._cancel_signal:
            return

        while not kill_switch.wait(timeout=0.1):
            if self._cancel_signal.is_set():
                self._emit_node_cancellation_events(
                    error_message="Workflow run cancelled",
                )

                captured_stacktrace = "".join(traceback.format_stack())
                self._workflow_event_outer_queue.put(
                    self._reject_workflow_event(
                        WorkflowError(
                            code=WorkflowErrorCode.WORKFLOW_CANCELLED,
                            message="Workflow run cancelled",
                        ),
                        captured_stacktrace,
                    )
                )
                return

    def _run_timeout_thread(self, kill_switch: ThreadingEvent) -> None:
        if not self._timeout:
            return

        if kill_switch.wait(timeout=self._timeout):
            return

        self._emit_node_cancellation_events(
            error_message=f"Workflow execution exceeded timeout of {self._timeout} seconds",
        )

        captured_stacktrace = "".join(traceback.format_stack())
        self._workflow_event_outer_queue.put(
            self._reject_workflow_event(
                WorkflowError(
                    code=WorkflowErrorCode.WORKFLOW_TIMEOUT,
                    message=f"Workflow execution exceeded timeout of {self._timeout} seconds",
                ),
                captured_stacktrace,
            )
        )

    def _is_terminal_event(self, event: WorkflowEvent) -> bool:
        if (
            event.name == "workflow.execution.fulfilled"
            or event.name == "workflow.execution.rejected"
            or event.name == "workflow.execution.paused"
        ):
            return event.workflow_definition == self.workflow.__class__
        return False

    def _generate_events(self) -> Generator[WorkflowEvent, None, None]:
        self._background_thread = Thread(
            target=self._run_background_thread,
            name=f"{self.workflow.__class__.__name__}.background_thread",
        )
        self._background_thread.start()

        cancel_thread_kill_switch = ThreadingEvent()
        if self._cancel_signal:
            self._cancel_thread = Thread(
                target=self._run_cancel_thread,
                name=f"{self.workflow.__class__.__name__}.cancel_thread",
                kwargs={"kill_switch": cancel_thread_kill_switch},
            )
            self._cancel_thread.start()

        timeout_thread_kill_switch = ThreadingEvent()
        if self._timeout:
            self._timeout_thread = Thread(
                target=self._run_timeout_thread,
                name=f"{self.workflow.__class__.__name__}.timeout_thread",
                kwargs={"kill_switch": timeout_thread_kill_switch},
            )
            self._timeout_thread.start()

        event: WorkflowEvent
        if self._is_resuming:
            event = self._resume_workflow_event()
        else:
            event = self._initiate_workflow_event()

        yield self._emit_event(event)

        # The extra level of indirection prevents the runner from waiting on the caller to consume the event stream
        self._stream_thread = Thread(
            target=self._wrapped_stream,
            name=f"{self.workflow.__class__.__name__}.stream_thread",
        )
        self._stream_thread.start()

        while self._stream_thread.is_alive():
            try:
                event = self._workflow_event_outer_queue.get(timeout=0.1)
            except Empty:
                continue

            yield self._emit_event(event)

            if self._is_terminal_event(event):
                break

        try:
            while event := self._workflow_event_outer_queue.get_nowait():
                yield self._emit_event(event)
        except Empty:
            pass

        if not self._is_terminal_event(event):
            yield self._reject_workflow_event(
                WorkflowError(
                    code=WorkflowErrorCode.INTERNAL_ERROR,
                    message="An unexpected error occurred while streaming Workflow events",
                )
            )

        self._background_thread_queue.put(None)
        cancel_thread_kill_switch.set()
        timeout_thread_kill_switch.set()

    def stream(self) -> WorkflowEventStream:
        return WorkflowEventGenerator(self._generate_events(), self._initial_state.meta.span_id)

    def join(self) -> None:
        """
        Wait for all background threads to complete.
        This ensures all pending work is finished before the runner terminates.
        """
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join()

        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join()

        if self._cancel_thread and self._cancel_thread.is_alive():
            self._cancel_thread.join()

        if self._timeout_thread and self._timeout_thread.is_alive():
            self._timeout_thread.join()
