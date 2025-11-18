from typing import List, Union

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, TestDatasetRowIdSerializationWorkflow

if __name__ == "__main__":
    raise Exception("This file is not meant to be imported")

dataset: List[Union[BaseInputs, DatasetRow]] = [
    DatasetRow(id="dataset-row-id-1", label="Scenario 1", inputs=Inputs(message="World")),
    DatasetRow(id="dataset-row-id-2", label="Scenario 2", inputs=Inputs(message="Test")),
    DatasetRow(label="Scenario 3 without ID", inputs=Inputs(message="No ID")),
]

runner = WorkflowSandboxRunner(workflow=TestDatasetRowIdSerializationWorkflow(), dataset=dataset)

runner.run()
