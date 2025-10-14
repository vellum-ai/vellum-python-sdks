from typing import List, Union

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, TestDatasetArraySerializationWorkflow

if __name__ == "__main__":
    raise Exception("This file is not meant to be imported")

dataset: List[Union[BaseInputs, DatasetRow]] = [
    Inputs(tags=["python", "typescript", "javascript"]),
    DatasetRow(label="Backend Tags", inputs=Inputs(tags=["django", "flask", "fastapi"])),
    DatasetRow(label="Frontend Tags", inputs=Inputs(tags=["react", "vue", "angular"])),
]

runner = WorkflowSandboxRunner(workflow=TestDatasetArraySerializationWorkflow(), dataset=dataset)

runner.run()
