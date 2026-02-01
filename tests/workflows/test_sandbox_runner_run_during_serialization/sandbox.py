from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, RunnerRunDuringSerializationWorkflow

dataset = [
    DatasetRow(
        label="Scenario 1",
        inputs=Inputs(message="hello"),
    ),
]

runner = WorkflowSandboxRunner(workflow=RunnerRunDuringSerializationWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()

runner.run()
