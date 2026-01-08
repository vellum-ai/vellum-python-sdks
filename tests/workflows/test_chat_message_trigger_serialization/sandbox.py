from vellum.workflows.inputs import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .triggers.chat import Chat
from .workflow import Workflow

dataset = [
    DatasetRow(label="New conversation", workflow_trigger=Chat(message="I want to tweet about AI agents")),
]

runner = WorkflowSandboxRunner(workflow=Workflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
