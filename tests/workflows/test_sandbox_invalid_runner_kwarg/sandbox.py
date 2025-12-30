from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, InvalidRunnerKwargWorkflow

# This sandbox.py has an invalid kwarg 'scenarios' on WorkflowSandboxRunner
# The correct kwarg is 'dataset', not 'scenarios'
scenarios = [
    DatasetRow(
        label="Scenario 1",
        inputs=Inputs(message="hello"),
    ),
]

runner = WorkflowSandboxRunner(workflow=InvalidRunnerKwargWorkflow(), scenarios=scenarios)  # type: ignore[call-arg]

if __name__ == "__main__":
    runner.run()
