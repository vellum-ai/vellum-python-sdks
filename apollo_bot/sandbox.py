from vellum.workflows.inputs import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .inputs import Inputs
from .workflow import Workflow

dataset = [
    DatasetRow(
        label="Tagged Message",
        inputs=Inputs(slack_url="https://vellum-ai.slack.com/archives/C08H3J7HUUT/p1759791207673199"),
    ),
    DatasetRow(
        label="Not Tagged Message",
        inputs=Inputs(slack_url="https://example.slack.com/archives/C1234567890/p9876543210987654"),
    ),
]

runner = WorkflowSandboxRunner(workflow=Workflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
