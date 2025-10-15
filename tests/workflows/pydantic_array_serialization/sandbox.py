from typing import List, Union

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import CustomItem, Inputs, PydanticArrayWorkflow

dataset: List[Union[BaseInputs, DatasetRow]] = [
    Inputs(
        items=[
            CustomItem(name="item1", value=10, is_active=True),
            CustomItem(name="item2", value=20, is_active=False),
            CustomItem(name="item3", value=30),
        ]
    ),
    DatasetRow(
        label="Custom Test",
        inputs=Inputs(
            items=[
                CustomItem(name="test1", value=100),
                CustomItem(name="test2", value=200, is_active=False),
            ]
        ),
    ),
]

runner = WorkflowSandboxRunner(workflow=PydanticArrayWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
