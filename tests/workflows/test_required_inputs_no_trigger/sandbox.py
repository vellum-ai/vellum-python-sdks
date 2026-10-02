from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import TestRequiredInputsNoTriggerWorkflow

dataset = [
    DatasetRow(label="Scenario 1"),
]

runner = WorkflowSandboxRunner(workflow=TestRequiredInputsNoTriggerWorkflow(), dataset=dataset)
