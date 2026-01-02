import sys
from uuid import uuid4

from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


def test_serialize_module__dataset_mocks_are_stable():
    """
    Tests that serialization produces stable, deterministic output for DatasetRow mocks
    across multiple serializations.
    """

    # GIVEN a workflow module with a sandbox.py that has DatasetRow with mocks
    files = {
        "__init__.py": "",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    message: str


class CodeExecution(BaseNode[BaseState]):
    class Outputs(BaseNode.Outputs):
        result: str
        log: str

    def run(self) -> Outputs:
        return self.Outputs(result="executed", log="")


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = CodeExecution

    class Outputs(BaseWorkflow.Outputs):
        final_result = CodeExecution.Outputs.result
""",
        "sandbox.py": """\
from vellum.workflows import DatasetRow

from .workflow import CodeExecution, Inputs

dataset = [
    DatasetRow(
        label="With mocked code node",
        inputs=Inputs(message="hello"),
        mocks=[
            CodeExecution.Outputs(result="MOCKED_RESULT", log=""),
        ],
    ),
]
""",
    }

    # AND two different namespaces (simulating how the workflow server creates a new namespace per request)
    namespace_1 = str(uuid4())
    namespace_2 = str(uuid4())

    # AND the virtual file loaders are registered for both namespaces
    sys.meta_path.append(VirtualFileFinder(files, namespace_1))
    sys.meta_path.append(VirtualFileFinder(files, namespace_2))

    try:
        # WHEN we serialize the module with different namespaces (like the workflow server does)
        result_1 = BaseWorkflowDisplay.serialize_module(namespace_1)
        result_2 = BaseWorkflowDisplay.serialize_module(namespace_2)

        # THEN both serializations should succeed without errors
        assert len(result_1.errors) == 0, f"First serialization had errors: {result_1.errors}"
        assert len(result_2.errors) == 0, f"Second serialization had errors: {result_2.errors}"

        # AND both should have a dataset
        assert result_1.dataset is not None, "First serialization should have a dataset"
        assert result_2.dataset is not None, "Second serialization should have a dataset"

        # AND the datasets should be identical (stable serialization)
        assert result_1.dataset == result_2.dataset, (
            f"Datasets should be identical across serializations.\n"
            f"First: {result_1.dataset}\n"
            f"Second: {result_2.dataset}"
        )
    finally:
        # Clean up the virtual file finders
        sys.meta_path = [finder for finder in sys.meta_path if not isinstance(finder, VirtualFileFinder)]
