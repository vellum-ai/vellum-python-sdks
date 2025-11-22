from typing import List, Union

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.nodes.mocks import MockNodeExecution
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, NodeOutputMockWhenConditionsWorkflow, ProcessNode

dataset: List[Union[BaseInputs, DatasetRow]] = [
    DatasetRow(
        label="Scenario 1",
        inputs=Inputs(threshold=5),
        node_output_mocks=[
            MockNodeExecution(
                when_condition=(Inputs.threshold.equals(5) & ProcessNode.Execution.count.equals(0)),
                then_outputs=ProcessNode.Outputs(result="first_execution_threshold_5"),
            ),
            MockNodeExecution(
                when_condition=(Inputs.threshold.equals(5) & ProcessNode.Execution.count.equals(1)),
                then_outputs=ProcessNode.Outputs(result="second_execution_threshold_5"),
            ),
        ],
    ),
    DatasetRow(
        label="Scenario 2",
        inputs=Inputs(threshold=10),
        node_output_mocks=[
            MockNodeExecution(
                when_condition=(Inputs.threshold.equals(10) & ProcessNode.Execution.count.equals(0)),
                then_outputs=ProcessNode.Outputs(result="first_execution_threshold_10"),
            ),
        ],
    ),
]

runner = WorkflowSandboxRunner(workflow=NodeOutputMockWhenConditionsWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
