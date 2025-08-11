from typing import Generic, Optional, Sequence

import dotenv

from vellum.workflows.events.workflow import WorkflowEventStream
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.logging import load_logger
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.workflows.event_filters import root_workflow_event_filter


class WorkflowSandboxRunner(Generic[WorkflowType]):
    def __init__(
        self,
        workflow: WorkflowType,
        inputs: Optional[Sequence[BaseInputs]] = None,  # DEPRECATED - remove in v2.0.0
        dataset: Optional[Sequence[BaseInputs]] = None,
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
        if index < 0:
            self._logger.warning("Index is less than 0, running first input")
            index = 0
        elif index >= len(self._inputs):
            self._logger.warning("Index is greater than the number of provided inputs, running last input")
            index = len(self._inputs) - 1

        selected_inputs = self._inputs[index]

        events = self._workflow.stream(
            inputs=selected_inputs,
            event_filter=root_workflow_event_filter,
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
