from typing import List, Union

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, TestDatasetSerializationWorkflow

dataset: List[Union[BaseInputs, DatasetRow]] = [
    Inputs(message="World"),
    DatasetRow(label="Custom Test", inputs=Inputs(message="DatasetRow Test")),
]

runner = WorkflowSandboxRunner(workflow=TestDatasetSerializationWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
