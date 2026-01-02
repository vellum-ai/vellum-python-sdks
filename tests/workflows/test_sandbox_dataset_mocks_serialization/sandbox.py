from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import CodeExecution, Inputs, MocksSerializationWorkflow

dataset = [
    DatasetRow(
        label="With mocked code node",
        inputs=Inputs(message="hello"),
        mocks=[
            CodeExecution.Outputs(result="MOCKED_RESULT", log=""),
        ],
    ),
]

runner = WorkflowSandboxRunner(workflow=MocksSerializationWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
