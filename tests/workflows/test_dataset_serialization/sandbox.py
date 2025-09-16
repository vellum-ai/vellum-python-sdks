from typing import List, Union

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, TestDatasetSerializationWorkflow

if __name__ == "__main__":
    raise Exception("This file is not meant to be imported")

dataset: List[Union[BaseInputs, DatasetRow]] = [
    Inputs(message="World"),
    DatasetRow(label="Custom Test", inputs=Inputs(message="DatasetRow Test")),
]

runner = WorkflowSandboxRunner(workflow=TestDatasetSerializationWorkflow(), dataset=dataset)

runner.run()
