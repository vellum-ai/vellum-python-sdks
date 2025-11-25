from datetime import datetime
from typing import List

from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import MySchedule, TestDatasetWithTriggerSerializationWorkflow

if __name__ == "__main__":
    raise Exception("This file is not meant to be imported")

dataset: List[DatasetRow] = [
    DatasetRow(
        label="Scenario 1",
        inputs=[],
        workflow_trigger=MySchedule(current_run_at=datetime.min, next_run_at=datetime.now()),
    ),
]

runner = WorkflowSandboxRunner(workflow=TestDatasetWithTriggerSerializationWorkflow(), dataset=dataset)

runner.run()
