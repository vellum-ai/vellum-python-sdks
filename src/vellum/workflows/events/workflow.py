import logging
from uuid import UUID
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterable, Literal, Optional, Type, Union
from typing_extensions import TypeGuard

from pydantic import SerializationInfo, field_serializer

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.workflows.errors import WorkflowError
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.references import ExternalInputReference
from vellum.workflows.types.definition import serialize_type_encoder_with_id
from vellum.workflows.types.generics import InputsType, OutputsType, StateType

from .node import (
    NodeExecutionFulfilledEvent,
    NodeExecutionInitiatedEvent,
    NodeExecutionPausedEvent,
    NodeExecutionRejectedEvent,
    NodeExecutionResumedEvent,
    NodeExecutionStreamingEvent,
)
from .stream import WorkflowEventGenerator
from .types import BaseEvent, default_serializer

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


class _BaseWorkflowExecutionBody(UniversalBaseModel):
    workflow_definition: Type["BaseWorkflow"]

    @field_serializer("workflow_definition")
    def serialize_workflow_definition(self, workflow_definition: Type, _info: Any) -> Dict[str, Any]:
        return serialize_type_encoder_with_id(workflow_definition)


class _BaseWorkflowEvent(BaseEvent):
    body: _BaseWorkflowExecutionBody

    @property
    def workflow_definition(self) -> Type["BaseWorkflow"]:
        return self.body.workflow_definition

    @property
    def monitoring_url(self) -> Optional[str]:
        """
        Get the monitoring URL for this workflow execution.

        Returns:
            The URL to view execution details in Vellum UI, or None if monitoring is disabled
            or context is not available.
        """
        return None


class NodeEventDisplayContext(UniversalBaseModel):
    input_display: Dict[str, UUID]
    output_display: Dict[str, UUID]
    port_display: Dict[str, UUID]
    subworkflow_display: Optional["WorkflowEventDisplayContext"] = None


class WorkflowEventDisplayContext(UniversalBaseModel):
    node_displays: Dict[UUID, NodeEventDisplayContext]
    workflow_inputs: Dict[str, UUID]
    workflow_outputs: Dict[str, UUID]


class WorkflowExecutionInitiatedBody(_BaseWorkflowExecutionBody, Generic[InputsType, StateType]):
    inputs: InputsType
    initial_state: Optional[StateType] = None

    # It is still the responsibility of the workflow server to populate this context. The SDK's
    # Workflow Runner will always leave this field None.
    #
    # It's conceivable in a future where all `id`s are agnostic to display and reside in a third location,
    # that the Workflow Runner can begin populating this field then.
    display_context: Optional[WorkflowEventDisplayContext] = None

    # This field will be populated during serialization by the serialize_body method
    workflow_version_exec_config: Optional[Any] = None

    # This field can be populated with arbitrary server metadata during event enrichment
    server_metadata: Optional[Dict[str, Any]] = None

    @field_serializer("inputs")
    def serialize_inputs(self, inputs: InputsType, _info: Any) -> Dict[str, Any]:
        return default_serializer(inputs)

    @field_serializer("initial_state")
    def serialize_initial_state(self, initial_state: Optional[StateType], _info: Any) -> Optional[Dict[str, Any]]:
        return default_serializer(initial_state)


class WorkflowExecutionInitiatedEvent(_BaseWorkflowEvent, Generic[InputsType, StateType]):
    name: Literal["workflow.execution.initiated"] = "workflow.execution.initiated"
    body: WorkflowExecutionInitiatedBody[InputsType, StateType]

    @property
    def inputs(self) -> InputsType:
        return self.body.inputs

    @property
    def initial_state(self) -> Optional[StateType]:
        return self.body.initial_state

    @field_serializer("body")
    def serialize_body(
        self, body: WorkflowExecutionInitiatedBody[InputsType, StateType], info: SerializationInfo
    ) -> WorkflowExecutionInitiatedBody[InputsType, StateType]:
        context = info.context if info and hasattr(info, "context") else {}
        if context and "event_enricher" in context and callable(context["event_enricher"]):
            try:
                event = context["event_enricher"](self)
                return event.body
            except Exception as e:
                logger.exception(f"Error in event_enricher: {e}")
                return body
        else:
            return body


class WorkflowExecutionStreamingBody(_BaseWorkflowExecutionBody):
    output: BaseOutput

    @field_serializer("output")
    def serialize_output(self, output: BaseOutput, _info: Any) -> Dict[str, Any]:
        return default_serializer(output)


class WorkflowExecutionStreamingEvent(_BaseWorkflowEvent):
    name: Literal["workflow.execution.streaming"] = "workflow.execution.streaming"
    body: WorkflowExecutionStreamingBody

    @property
    def output(self) -> BaseOutput:
        return self.body.output


class WorkflowExecutionFulfilledBody(_BaseWorkflowExecutionBody, Generic[OutputsType, StateType]):
    outputs: OutputsType
    final_state: Optional[StateType] = None

    @field_serializer("outputs")
    def serialize_outputs(self, outputs: OutputsType, _info: Any) -> Dict[str, Any]:
        return default_serializer(outputs)

    @field_serializer("final_state")
    def serialize_final_state(self, final_state: Optional[StateType], _info: Any) -> Optional[Dict[str, Any]]:
        if final_state is None:
            return None
        state_dict = {k: v for k, v in final_state if k != "meta"}
        return default_serializer(state_dict)


class WorkflowExecutionFulfilledEvent(_BaseWorkflowEvent, Generic[OutputsType, StateType]):
    name: Literal["workflow.execution.fulfilled"] = "workflow.execution.fulfilled"
    body: WorkflowExecutionFulfilledBody[OutputsType, StateType]

    @property
    def outputs(self) -> OutputsType:
        return self.body.outputs

    @property
    def final_state(self) -> Optional[StateType]:
        return self.body.final_state


class WorkflowExecutionRejectedBody(_BaseWorkflowExecutionBody):
    error: WorkflowError
    stacktrace: Optional[str] = None


class WorkflowExecutionRejectedEvent(_BaseWorkflowEvent):
    name: Literal["workflow.execution.rejected"] = "workflow.execution.rejected"
    body: WorkflowExecutionRejectedBody

    @property
    def error(self) -> WorkflowError:
        return self.body.error


class WorkflowExecutionPausedBody(_BaseWorkflowExecutionBody):
    external_inputs: Iterable[ExternalInputReference]


class WorkflowExecutionPausedEvent(_BaseWorkflowEvent):
    name: Literal["workflow.execution.paused"] = "workflow.execution.paused"
    body: WorkflowExecutionPausedBody

    @property
    def external_inputs(self) -> Iterable[ExternalInputReference]:
        return self.body.external_inputs


class WorkflowExecutionResumedBody(_BaseWorkflowExecutionBody):
    pass


class WorkflowExecutionResumedEvent(_BaseWorkflowEvent):
    name: Literal["workflow.execution.resumed"] = "workflow.execution.resumed"
    body: WorkflowExecutionResumedBody


class WorkflowExecutionSnapshottedBody(_BaseWorkflowExecutionBody, Generic[StateType]):
    state: StateType

    @field_serializer("state")
    def serialize_state(self, state: StateType, _info: Any) -> Dict[str, Any]:
        return default_serializer(state)


class WorkflowExecutionSnapshottedEvent(_BaseWorkflowEvent, Generic[StateType]):
    name: Literal["workflow.execution.snapshotted"] = "workflow.execution.snapshotted"
    body: WorkflowExecutionSnapshottedBody[StateType]

    @property
    def state(self) -> StateType:
        return self.body.state


GenericWorkflowEvent = Union[
    WorkflowExecutionStreamingEvent,
    WorkflowExecutionRejectedEvent,
    WorkflowExecutionPausedEvent,
    WorkflowExecutionResumedEvent,
    NodeExecutionInitiatedEvent,
    NodeExecutionStreamingEvent,
    NodeExecutionFulfilledEvent,
    NodeExecutionRejectedEvent,
    NodeExecutionPausedEvent,
    NodeExecutionResumedEvent,
]

WorkflowEvent = Union[
    GenericWorkflowEvent,
    WorkflowExecutionInitiatedEvent,
    WorkflowExecutionFulfilledEvent,
    WorkflowExecutionSnapshottedEvent,
]

WorkflowEventStream = WorkflowEventGenerator[WorkflowEvent]

WorkflowExecutionEvent = Union[
    WorkflowExecutionInitiatedEvent,
    WorkflowExecutionStreamingEvent,
    WorkflowExecutionRejectedEvent,
    WorkflowExecutionPausedEvent,
    WorkflowExecutionResumedEvent,
    WorkflowExecutionFulfilledEvent,
    WorkflowExecutionSnapshottedEvent,
]

TerminalWorkflowExecutionEvent = Union[
    WorkflowExecutionFulfilledEvent,
    WorkflowExecutionRejectedEvent,
    WorkflowExecutionPausedEvent,
]


def is_workflow_event(event: WorkflowEvent) -> TypeGuard[WorkflowExecutionEvent]:
    return (
        event.name == "workflow.execution.initiated"
        or event.name == "workflow.execution.fulfilled"
        or event.name == "workflow.execution.streaming"
        or event.name == "workflow.execution.snapshotted"
        or event.name == "workflow.execution.paused"
        or event.name == "workflow.execution.resumed"
        or event.name == "workflow.execution.rejected"
    )


def is_terminal_workflow_execution_event(event: WorkflowEvent) -> TypeGuard[TerminalWorkflowExecutionEvent]:
    return (
        event.name == "workflow.execution.fulfilled"
        or event.name == "workflow.execution.rejected"
        or event.name == "workflow.execution.paused"
    )
