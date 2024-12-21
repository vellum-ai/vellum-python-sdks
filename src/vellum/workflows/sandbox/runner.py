from typing import Generic, List, Optional, Type

import dotenv

from vellum.workflows.events.workflow import WorkflowEventStream
from vellum.workflows.logging import load_logger
from vellum.workflows.sandbox.types import Datapoint
from vellum.workflows.types.generics import WorkflowType
from vellum.workflows.workflows.event_filters import root_workflow_event_filter


class SandboxRunner(Generic[WorkflowType]):
    def __init__(self, workflow: Type[WorkflowType], dataset: List[Datapoint]):
        if not dataset:
            raise ValueError("Dataset is required to have at least one datapoint")

        self._workflow = workflow
        self._dataset = dataset

        dotenv.load_dotenv()
        self._logger = load_logger()

    def run(self, datapoint: Optional[str] = None):
        selected_datapoint = next((d for d in self._dataset if d.name == datapoint), self._dataset[0])
        self._logger.info(f"Running dataset: {selected_datapoint.name}")

        workflow = self._workflow()
        events = workflow.stream(
            inputs=selected_datapoint.inputs,
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
