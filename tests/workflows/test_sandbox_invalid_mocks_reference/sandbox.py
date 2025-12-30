from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import CodeExecution, Inputs, InvalidMocksReferenceWorkflow

# This sandbox.py has an invalid reference to CodeExecution.Mocks.Outputs
# which doesn't exist - nodes don't have a Mocks nested class
dataset = [
    DatasetRow(
        label="Scenario 1",
        inputs=Inputs(message="hello"),
        mocks=[
            CodeExecution.Mocks.Outputs(result="mocked result"),  # type: ignore[attr-defined]
        ],
    ),
]

runner = WorkflowSandboxRunner(workflow=InvalidMocksReferenceWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
