from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, TestDatasetSerializationWorkflow

if __name__ == "__main__":
    raise Exception("This file is not meant to be imported")

dataset = [
    Inputs(message="World"),
    Inputs(message="Test"),
]

runner = WorkflowSandboxRunner(workflow=TestDatasetSerializationWorkflow(), dataset=dataset)

runner.run()
