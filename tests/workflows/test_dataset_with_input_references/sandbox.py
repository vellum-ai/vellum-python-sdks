from typing import List, Type

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, TestDatasetWithInputReferencesWorkflow

dataset: List[Type[BaseInputs]] = [
    Inputs,
]

runner = WorkflowSandboxRunner(workflow=TestDatasetWithInputReferencesWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
