from vellum.client.types import VellumDocument
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, InvalidPdfDataUrlWorkflow

dataset = [
    DatasetRow(
        label="Scenario with invalid PDF",
        inputs=Inputs(
            document=VellumDocument(src="data:application/pdf;base64,not-valid-base64!!!"),
        ),
    ),
]

runner = WorkflowSandboxRunner(workflow=InvalidPdfDataUrlWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
