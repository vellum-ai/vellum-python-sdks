from contextvars import ContextVar, Token
import traceback
from typing import Any, Dict, Generic, List, Optional, Sequence, Tuple, Union

import dotenv

from vellum.workflows.events.workflow import WorkflowEventStream
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.logging import load_logger
from vellum.workflows.triggers.base import BaseTrigger
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

_serialization_context: ContextVar[bool] = ContextVar("_serialization_context", default=False)
_serialization_errors: ContextVar[Optional[List[Tuple[Exception, str]]]] = ContextVar(
    "_serialization_errors", default=None
)


def is_in_serialization_context() -> bool:
    """Check if we're currently in a serialization context."""
    return _serialization_context.get()


def enter_serialization_context() -> Tuple[Token[bool], Token[Optional[List[Tuple[Exception, str]]]]]:
    """Enter serialization context and return tokens for cleanup."""
    context_token = _serialization_context.set(True)
    errors_token = _serialization_errors.set([])
    return context_token, errors_token


def exit_serialization_context(
    context_token: Token[bool], errors_token: Token[Optional[List[Tuple[Exception, str]]]]
) -> List[Tuple[Exception, str]]:
    """Exit serialization context and return any recorded errors."""
    errors = _serialization_errors.get() or []
    _serialization_context.reset(context_token)
    _serialization_errors.reset(errors_token)
    return list(errors)


def _record_serialization_error(error: Exception, stacktrace: str) -> None:
    """Record an error that occurred during serialization."""
    errors = _serialization_errors.get()
    if errors is not None:
        errors.append((error, stacktrace))


class WorkflowSandboxRunner(Generic[WorkflowType]):
    def __init__(
        self,
        workflow: WorkflowType,
        inputs: Optional[Sequence[BaseInputs]] = None,  # DEPRECATED - remove in v2.0.0
        dataset: Optional[Sequence[Union[BaseInputs, DatasetRow]]] = None,
    ):
        dotenv.load_dotenv()
        self._logger = load_logger()

        if dataset is not None and inputs is not None:
            raise ValueError(
                "Cannot specify both 'dataset' and 'inputs' parameters. " "Use 'dataset' as 'inputs' is deprecated."
            )

        if dataset is not None:
            actual_inputs = dataset
        elif inputs is not None:
            self._logger.warning(
                "The 'inputs' parameter is deprecated and will be removed in v2.0.0. " "Please use 'dataset' instead."
            )
            actual_inputs = inputs
        else:
            raise ValueError("Either 'dataset' or 'inputs' parameter is required")

        if not actual_inputs:
            raise ValueError("Dataset/inputs are required to have at least one defined input")

        self._workflow = workflow
        self._inputs = actual_inputs

    def run(self, index: int = 0):
        if is_in_serialization_context():
            error = RuntimeError(
                "runner.run() should not be called during serialization. "
                "Move the runner.run() call inside an 'if __name__ == \"__main__\":' block."
            )
            stacktrace = "".join(traceback.format_stack())
            _record_serialization_error(error, stacktrace)
            return

        if index < 0:
            self._logger.warning("Index is less than 0, running first input")
            index = 0
        elif index >= len(self._inputs):
            self._logger.warning("Index is greater than the number of provided inputs, running last input")
            index = len(self._inputs) - 1

        selected_inputs = self._inputs[index]

        raw_inputs: Union[BaseInputs, Dict[str, Any]]
        trigger_value: Optional[BaseTrigger] = None
        node_output_mocks = None
        if isinstance(selected_inputs, DatasetRow):
            raw_inputs = selected_inputs.inputs
            trigger_value = selected_inputs.workflow_trigger
            node_output_mocks = selected_inputs.mocks
        else:
            raw_inputs = selected_inputs

        inputs_for_stream: BaseInputs
        if isinstance(raw_inputs, dict):
            inputs_class = type(self._workflow).get_inputs_class()
            inputs_for_stream = inputs_class(**raw_inputs)
        else:
            inputs_for_stream = raw_inputs

        trigger_instance: Optional[BaseTrigger] = trigger_value

        events = self._workflow.stream(
            inputs=inputs_for_stream,
            event_filter=root_workflow_event_filter,
            trigger=trigger_instance,
            node_output_mocks=node_output_mocks,
        )

        self._process_events(events)

    def _process_events(self, events: WorkflowEventStream):
        for event in events:
            if event.name == "workflow.execution.fulfilled":
                self._logger.info("Workflow fulfilled!")
                for output_reference, value in event.outputs:
                    self._logger.info("----------------------------------")
                    self._logger.info(f"{output_reference.name}: {value}")
            elif event.name == "node.execution.initiated":
                self._logger.info(f"Just started Node: {event.node_definition.__name__}")
            elif event.name == "node.execution.fulfilled":
                self._logger.info(f"Just finished Node: {event.node_definition.__name__}")
            elif event.name == "node.execution.rejected":
                self._logger.debug(f"Error: {event.error}")
                self._logger.error(f"Failed to run Node: {event.node_definition.__name__}")
            elif event.name == "workflow.execution.rejected":
                self._logger.error(f"Workflow rejected! Error: {event.error}")
