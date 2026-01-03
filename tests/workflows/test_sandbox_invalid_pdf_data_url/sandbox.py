import base64

from vellum.client.types import VellumDocument
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.sandbox import WorkflowSandboxRunner

from .workflow import Inputs, InvalidPdfDataUrlWorkflow

# Valid base64 encoded content for the second dataset row
VALID_PDF_CONTENT = base64.b64encode(b"Valid PDF content").decode("utf-8")

dataset = [
    DatasetRow(
        label="Scenario with invalid PDF",
        inputs=Inputs(
            document=VellumDocument(src="data:application/pdf;base64,not-valid-base64!!!"),
            name="Test User",
        ),
    ),
    DatasetRow(
        label="Scenario with valid PDF",
        inputs=Inputs(
            document=VellumDocument(src=f"data:application/pdf;base64,{VALID_PDF_CONTENT}"),
            name="Another User",
        ),
    ),
]

runner = WorkflowSandboxRunner(workflow=InvalidPdfDataUrlWorkflow(), dataset=dataset)

if __name__ == "__main__":
    runner.run()
