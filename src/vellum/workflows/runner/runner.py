from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
import logging
from queue import Empty, Queue
from threading import Event as ThreadingEvent, Thread
from uuid import UUID
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterable, Iterator, Optional, Sequence, Set, Tuple, Type, Union

from vellum.workflows.constants import undefined
from vellum.workflows.context import ExecutionContext, execution_context, get_execution_context, get_parent_context
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.edges.edge import Edge
from vellum.workflows.errors import WorkflowError, WorkflowErrorCode
from vellum.workflows.events import (
    NodeExecutionFulfilledEvent,
    NodeExecutionInitiatedEvent,
    NodeExecutionRejectedEvent,
    NodeExecutionStreamingEvent,
    WorkflowEvent,
    WorkflowEventStream,
    WorkflowExecutionFulfilledEvent,
    WorkflowExecutionInitiatedEvent,
    WorkflowExecutionRejectedEvent,
    WorkflowExecutionStreamingEvent,
)
from vellum.workflows.events.node import (
    NodeExecutionFulfilledBody,
    NodeExecutionInitiatedBody,
    NodeExecutionRejectedBody,
    NodeExecutionStreamingBody,
)
from vellum.workflows.events.types import BaseEvent, NodeParentContext, WorkflowParentContext
from vellum.workflows.events.workflow import (
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
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.generics import InputsType, OutputsType, StateType

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow

logger = logging.getLogger(__name__)

RunFromNodeArg = Sequence[Type[BaseNode]]
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
        cancel_signal: Optional[ThreadingEvent] = None,
        node_output_mocks: Optional[MockNodeExecutionArg] = None,
        max_concurrency: Optional[int] = None,
        init_execution_context: Optional[ExecutionContext] = None,
    ):
        if state and external_inputs:
            raise ValueError("Can only run a Workflow providing one of state or external inputs, not both")

        self.workflow = workflow
        self._is_resuming = False
        if entrypoint_nodes:
            if len(list(entrypoint_nodes)) > 1:
                raise ValueError("Cannot resume from multiple nodes")

            # TODO: Support resuming from multiple nodes
            # https://app.shortcut.com/vellum/story/4408
            node = next(iter(entrypoint_nodes))
            if state:
                self._initial_state = state
            else:
                self._initial_state = self.workflow.get_state_at_node(node)
            self._entrypoints = entrypoint_nodes
        elif external_inputs:
            self._initial_state = self.workflow.get_most_recent_state()
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
        else:
            normalized_inputs = deepcopy(inputs) if inputs else self.workflow.get_default_inputs()
            if state:
                self._initial_state = deepcopy(state)
                self._initial_state.meta.workflow_inputs = normalized_inputs
            else:
                self._initial_state = self.workflow.get_default_state(normalized_inputs)
            self._entrypoints = self.workflow.get_entrypoints()

        # This queue is responsible for sending events from WorkflowRunner to the outside world
        self._workflow_event_outer_queue: Queue[WorkflowEvent] = Queue()

        # This queue is responsible for sending events from the inner worker threads to WorkflowRunner
        self._workflow_event_inner_queue: Queue[WorkflowEvent] = Queue()

        self._max_concurrency = max_concurrency
        self._concurrency_queue: Queue[Tuple[StateType, Type[BaseNode], Optional[Edge]]] = Queue()

        # This queue is responsible for sending events from WorkflowRunner to the background thread
        # for user defined emitters
        self._background_thread_queue: Queue[BackgroundThreadItem] = Queue()

        self._dependencies: Dict[Type[BaseNode], Set[Type[BaseNode]]] = defaultdict(set)
        self._state_forks: Set[StateType] = {self._initial_state}

        self._active_nodes_by_execution_id: Dict[UUID, ActiveNode[StateType]] = {}
        self._cancel_signal = cancel_signal
        self._execution_context = init_execution_context or get_execution_context()
        self._parent_context = self._execution_context.parent_context

        setattr(
            self._initial_state,
            "__snapshot_callback__",
            lambda s: self._snapshot_state(s),
        )
        self.workflow.context._register_event_queue(self._workflow_event_inner_queue)
        self.workflow.context._register_node_output_mocks(node_output_mocks or [])

    def _snapshot_state(self, state: StateType) -> StateType:
        self._workflow_event_inner_queue.put(
            WorkflowExecutionSnapshottedEvent(
                trace_id=state.meta.trace_id,
                span_id=state.meta.span_id,
                body=WorkflowExecutionSnapshottedBody(
                    workflow_definition=self.workflow.__class__,
                    state=state,
                ),
                parent=self._parent_context,
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
        parent_context = get_parent_context()
        self._workflow_event_inner_queue.put(
            NodeExecutionInitiatedEvent(
                trace_id=node.state.meta.trace_id,
                span_id=span_id,
                body=NodeExecutionInitiatedBody(
                    node_definition=node.__class__,
                    inputs=node._inputs,
                ),
                parent=parent_context,
            )
        )

        logger.debug(f"Started running node: {node.__class__.__name__}")

        try:
            updated_parent_context = NodeParentContext(
                span_id=span_id,
                node_definition=node.__class__,
                parent=parent_context,
            )
            node_run_response: NodeRunResponse
            was_mocked: Optional[bool] = None
            mock_candidates = self.workflow.context.node_output_mocks_map.get(node.Outputs) or []
            for mock_candidate in mock_candidates:
                if mock_candidate.when_condition.resolve(node.state):
                    node_run_response = mock_candidate.then_outputs
                    was_mocked = True
                    break

            if not was_mocked:
                with execution_context(parent_context=updated_parent_context, trace_id=node.state.meta.trace_id):
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

                def initiate_node_streaming_output(output: BaseOutput) -> None:
                    parent_context = get_parent_context()
                    streaming_output_queues[output.name] = Queue()
                    output_descriptor = OutputReference(
                        name=output.name,
                        types=(type(output.delta),),
                        instance=None,
                        outputs_class=node.Outputs,
                    )
                    node.state.meta.node_outputs[output_descriptor] = streaming_output_queues[output.name]
                    initiated_output: BaseOutput = BaseOutput(name=output.name)
                    initiated_ports = initiated_output > ports
                    self._workflow_event_inner_queue.put(
                        NodeExecutionStreamingEvent(
                            trace_id=node.state.meta.trace_id,
                            span_id=span_id,
                            body=NodeExecutionStreamingBody(
                                node_definition=node.__class__,
                                output=initiated_output,
                                invoked_ports=initiated_ports,
                            ),
                            parent=parent_context,
                        ),
                    )

                with execution_context(parent_context=updated_parent_context, trace_id=node.state.meta.trace_id):
                    for output in node_run_response:
                        invoked_ports = output > ports
                        if output.is_initiated:
                            initiate_node_streaming_output(output)
                        elif output.is_streaming:
                            if output.name not in streaming_output_queues:
                                initiate_node_streaming_output(output)

                            streaming_output_queues[output.name].put(output.delta)
                            self._workflow_event_inner_queue.put(
                                NodeExecutionStreamingEvent(
                                    trace_id=node.state.meta.trace_id,
                                    span_id=span_id,
                                    body=NodeExecutionStreamingBody(
                                        node_definition=node.__class__,
                                        output=output,
                                        invoked_ports=invoked_ports,
                                    ),
                                    parent=parent_context,
                                ),
                            )
                        elif output.is_fulfilled:
                            if output.name in streaming_output_queues:
                                streaming_output_queues[output.name].put(undefined)

                            setattr(outputs, output.name, output.value)
                            self._workflow_event_inner_queue.put(
                                NodeExecutionStreamingEvent(
                                    trace_id=node.state.meta.trace_id,
                                    span_id=span_id,
                                    body=NodeExecutionStreamingBody(
                                        node_definition=node.__class__,
                                        output=output,
                                        invoked_ports=invoked_ports,
                                    ),
                                    parent=parent_context,
                                )
                            )

            node.state.meta.node_execution_cache.fulfill_node_execution(node.__class__, span_id)

            for descriptor, output_value in outputs:
                if output_value is undefined:
                    if descriptor in node.state.meta.node_outputs:
                        del node.state.meta.node_outputs[descriptor]
                    continue

                node.state.meta.node_outputs[descriptor] = output_value

            invoked_ports = ports(outputs, node.state)
            self._workflow_event_inner_queue.put(
                NodeExecutionFulfilledEvent(
                    trace_id=node.state.meta.trace_id,
                    span_id=span_id,
                    body=NodeExecutionFulfilledBody(
                        node_definition=node.__class__,
                        outputs=outputs,
                        invoked_ports=invoked_ports,
                        mocked=was_mocked,
                    ),
                    parent=parent_context,
                )
            )
        except NodeException as e:
            logger.info(e)
            self._workflow_event_inner_queue.put(
                NodeExecutionRejectedEvent(
                    trace_id=node.state.meta.trace_id,
                    span_id=span_id,
                    body=NodeExecutionRejectedBody(
                        node_definition=node.__class__,
                        error=e.error,
                    ),
                    parent=parent_context,
                )
            )
        except WorkflowInitializationException as e:
            logger.info(e)
            self._workflow_event_inner_queue.put(
                NodeExecutionRejectedEvent(
                    trace_id=node.state.meta.trace_id,
                    span_id=span_id,
                    body=NodeExecutionRejectedBody(
                        node_definition=node.__class__,
                        error=e.error,
                    ),
                    parent=parent_context,
                )
            )
        except Exception as e:
            logger.exception(f"An unexpected error occurred while running node {node.__class__.__name__}")

            self._workflow_event_inner_queue.put(
                NodeExecutionRejectedEvent(
                    trace_id=node.state.meta.trace_id,
                    span_id=span_id,
                    body=NodeExecutionRejectedBody(
                        node_definition=node.__class__,
                        error=WorkflowError(
                            message=str(e),
                            code=WorkflowErrorCode.INTERNAL_ERROR,
                        ),
                    ),
                    parent=parent_context,
                ),
            )

        logger.debug(f"Finished running node: {node.__class__.__name__}")

    def _context_run_work_item(self, node: BaseNode[StateType], span_id: UUID, parent_context=None) -> None:
        if parent_context is None:
            parent_context = get_parent_context() or self._parent_context

        with execution_context(parent_context=parent_context, trace_id=node.state.meta.trace_id):
            self._run_work_item(node, span_id)

    def _handle_invoked_ports(self, state: StateType, ports: Optional[Iterable[Port]]) -> None:
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
                    self._concurrency_queue.put((next_state, edge.to_node, edge))
                else:
                    self._run_node_if_ready(next_state, edge.to_node, edge)

        if self._max_concurrency:
            num_nodes_to_run = self._max_concurrency - len(self._active_nodes_by_execution_id)
            for _ in range(num_nodes_to_run):
                if self._concurrency_queue.empty():
                    break

                next_state, node_class, invoked_edge = self._concurrency_queue.get()
                self._run_node_if_ready(next_state, node_class, invoked_edge)

    def _run_node_if_ready(
        self,
        state: StateType,
        node_class: Type[BaseNode],
        invoked_by: Optional[Edge] = None,
    ) -> None:
        with state.__lock__:
            for descriptor in node_class.ExternalInputs:
                if not isinstance(descriptor, ExternalInputReference):
                    continue

                if state.meta.external_inputs.get(descriptor, undefined) is undefined:
                    state.meta.external_inputs[descriptor] = undefined
                    return

            all_deps = self._dependencies[node_class]
            node_span_id = state.meta.node_execution_cache.queue_node_execution(node_class, all_deps, invoked_by)
            if not node_class.Trigger.should_initiate(state, all_deps, node_span_id):
                return

            current_parent = get_parent_context()
            node = node_class(state=state, context=self.workflow.context)
            state.meta.node_execution_cache.initiate_node_execution(node_class, node_span_id)
            self._active_nodes_by_execution_id[node_span_id] = ActiveNode(node=node)

            worker_thread = Thread(
                target=self._context_run_work_item,
                kwargs={"node": node, "span_id": node_span_id, "parent_context": current_parent},
            )
            worker_thread.start()

    def _handle_work_item_event(self, event: WorkflowEvent) -> Optional[WorkflowError]:
        active_node = self._active_nodes_by_execution_id.get(event.span_id)
        if not active_node:
            return None

        node = active_node.node
        if event.name == "node.execution.rejected":
            self._active_nodes_by_execution_id.pop(event.span_id)
            return event.error

        if event.name == "node.execution.streaming":
            for workflow_output_descriptor in self.workflow.Outputs:
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

            self._handle_invoked_ports(node.state, event.invoked_ports)

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

            self._handle_invoked_ports(node.state, event.invoked_ports)

            return None

        return None

    def _initiate_workflow_event(self) -> WorkflowExecutionInitiatedEvent:
        return WorkflowExecutionInitiatedEvent(
            trace_id=self._initial_state.meta.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionInitiatedBody(
                workflow_definition=self.workflow.__class__,
                inputs=self._initial_state.meta.workflow_inputs,
            ),
            parent=self._parent_context,
        )

    def _stream_workflow_event(self, output: BaseOutput) -> WorkflowExecutionStreamingEvent:
        return WorkflowExecutionStreamingEvent(
            trace_id=self._initial_state.meta.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionStreamingBody(
                workflow_definition=self.workflow.__class__,
                output=output,
            ),
            parent=self._parent_context,
        )

    def _fulfill_workflow_event(self, outputs: OutputsType) -> WorkflowExecutionFulfilledEvent:
        return WorkflowExecutionFulfilledEvent(
            trace_id=self._initial_state.meta.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionFulfilledBody(
                workflow_definition=self.workflow.__class__,
                outputs=outputs,
            ),
            parent=self._parent_context,
        )

    def _reject_workflow_event(self, error: WorkflowError) -> WorkflowExecutionRejectedEvent:
        return WorkflowExecutionRejectedEvent(
            trace_id=self._initial_state.meta.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionRejectedBody(
                workflow_definition=self.workflow.__class__,
                error=error,
            ),
            parent=self._parent_context,
        )

    def _resume_workflow_event(self) -> WorkflowExecutionResumedEvent:
        return WorkflowExecutionResumedEvent(
            trace_id=self._initial_state.meta.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionResumedBody(
                workflow_definition=self.workflow.__class__,
            ),
        )

    def _pause_workflow_event(self, external_inputs: Iterable[ExternalInputReference]) -> WorkflowExecutionPausedEvent:
        return WorkflowExecutionPausedEvent(
            trace_id=self._initial_state.meta.trace_id,
            span_id=self._initial_state.meta.span_id,
            body=WorkflowExecutionPausedBody(
                workflow_definition=self.workflow.__class__,
                external_inputs=external_inputs,
            ),
            parent=self._parent_context,
        )

    def _stream(self) -> None:
        for edge in self.workflow.get_edges():
            self._dependencies[edge.to_node].add(edge.from_port.node_class)

        current_parent = WorkflowParentContext(
            span_id=self._initial_state.meta.span_id,
            workflow_definition=self.workflow.__class__,
            parent=self._parent_context,
            type="WORKFLOW",
        )
        for node_cls in self._entrypoints:
            try:
                if not self._max_concurrency or len(self._active_nodes_by_execution_id) < self._max_concurrency:
                    with execution_context(parent_context=current_parent, trace_id=self._initial_state.meta.trace_id):
                        self._run_node_if_ready(self._initial_state, node_cls)
                else:
                    self._concurrency_queue.put((self._initial_state, node_cls, None))
            except NodeException as e:
                self._workflow_event_outer_queue.put(self._reject_workflow_event(e.error))
                return
            except WorkflowInitializationException as e:
                self._workflow_event_outer_queue.put(self._reject_workflow_event(e.error))
                return
            except Exception:
                err_message = f"An unexpected error occurred while initializing node {node_cls.__name__}"
                logger.exception(err_message)
                self._workflow_event_outer_queue.put(
                    self._reject_workflow_event(
                        WorkflowError(code=WorkflowErrorCode.INTERNAL_ERROR, message=err_message),
                    )
                )
                return

        rejection_error: Optional[WorkflowError] = None

        while True:
            if not self._active_nodes_by_execution_id:
                break

            event = self._workflow_event_inner_queue.get()

            self._workflow_event_outer_queue.put(event)

            with execution_context(parent_context=current_parent, trace_id=self._initial_state.meta.trace_id):
                rejection_error = self._handle_work_item_event(event)

            if rejection_error:
                break

        # Handle any remaining events
        try:
            while event := self._workflow_event_inner_queue.get_nowait():
                self._workflow_event_outer_queue.put(event)

                with execution_context(parent_context=current_parent, trace_id=self._initial_state.meta.trace_id):
                    rejection_error = self._handle_work_item_event(event)

                if rejection_error:
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

        if rejection_error:
            self._workflow_event_outer_queue.put(self._reject_workflow_event(rejection_error))
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

        self._workflow_event_outer_queue.put(self._fulfill_workflow_event(fulfilled_outputs))

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
                self._workflow_event_outer_queue.put(
                    self._reject_workflow_event(
                        WorkflowError(
                            code=WorkflowErrorCode.WORKFLOW_CANCELLED,
                            message="Workflow run cancelled",
                        )
                    )
                )
                return

    def _is_terminal_event(self, event: WorkflowEvent) -> bool:
        if (
            event.name == "workflow.execution.fulfilled"
            or event.name == "workflow.execution.rejected"
            or event.name == "workflow.execution.paused"
        ):
            return event.workflow_definition == self.workflow.__class__
        return False

    def stream(self) -> WorkflowEventStream:
        background_thread = Thread(
            target=self._run_background_thread,
            name=f"{self.workflow.__class__.__name__}.background_thread",
        )
        background_thread.start()

        cancel_thread_kill_switch = ThreadingEvent()
        if self._cancel_signal:
            cancel_thread = Thread(
                target=self._run_cancel_thread,
                name=f"{self.workflow.__class__.__name__}.cancel_thread",
                kwargs={"kill_switch": cancel_thread_kill_switch},
            )
            cancel_thread.start()

        event: WorkflowEvent
        if self._is_resuming:
            event = self._resume_workflow_event()
        else:
            event = self._initiate_workflow_event()

        yield self._emit_event(event)

        # The extra level of indirection prevents the runner from waiting on the caller to consume the event stream
        stream_thread = Thread(
            target=self._stream,
            name=f"{self.workflow.__class__.__name__}.stream_thread",
        )
        stream_thread.start()

        while stream_thread.is_alive():
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
