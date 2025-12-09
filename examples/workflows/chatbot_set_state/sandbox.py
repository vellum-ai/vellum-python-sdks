from vellum.workflows.inputs import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

dataset = [
    DatasetRow(label="Scenario 1", inputs=Inputs(user_message="Hello")),
]

runner = WorkflowSandboxRunner(workflow=Workflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
