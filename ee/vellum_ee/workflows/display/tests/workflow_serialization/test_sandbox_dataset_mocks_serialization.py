import pytest
import sys
from uuid import uuid4
from typing import Callable

from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.server.namespaces import get_random_namespace
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder


def _generate_uuid_namespace() -> str:
    """Generate a UUID namespace like the workflow server uses for some requests."""
    return str(uuid4())


@pytest.mark.parametrize(
    "namespace_generator",
    [
        pytest.param(_generate_uuid_namespace, id="uuid_namespace"),
        pytest.param(get_random_namespace, id="workflow_tmp_namespace"),
    ],
)
def test_serialize_module__dataset_mocks_are_stable(namespace_generator: Callable[[], str]):
    """
    Tests that serialization produces stable, deterministic output for DatasetRow mocks
    across multiple serializations, regardless of the namespace format used.
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
    namespace_1 = namespace_generator()
    namespace_2 = namespace_generator()

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


def test_serialize_module__dataset_with_node_output_mocks_field_name():
    """
    Tests that DatasetRow with node_output_mocks field (legacy field name) properly
    serializes the mocks. This reproduces an issue where using node_output_mocks
    instead of mocks caused the dataset to return None for the mocks field.
    """

    # GIVEN a workflow module with parallel code execution nodes
    files = {
        "__init__.py": "",
        "inputs.py": """\
from typing import Any, Optional

from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    json: Optional[Any] = None
""",
        "nodes/__init__.py": "",
        "nodes/code_execution/__init__.py": """\
from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import MergeBehavior


class CodeExecution(CodeExecutionNode[BaseState, str]):
    filepath = "./script.py"
    code_inputs = {}
    runtime = "PYTHON_3_11_6"
    packages = []

    class Trigger(CodeExecutionNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES
""",
        "nodes/code_execution/script.py": '''\
"""
You must define a function called `main` whose arguments are named after the
Input Variables.
"""

def main() -> str:
    return "5".upper()
''',
        "nodes/code_execution_2/__init__.py": """\
from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import MergeBehavior


class CodeExecution2(CodeExecutionNode[BaseState, str]):
    filepath = "./script.py"
    code_inputs = {}
    runtime = "PYTHON_3_11_6"
    packages = []

    class Trigger(CodeExecutionNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES
""",
        "nodes/code_execution_2/script.py": '''\
"""
You must define a function called `main` whose arguments are named after the
Input Variables.
"""

def main() -> str:
    return "TODO"
''',
        "nodes/output.py": """\
from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState


class Output(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = None
""",
        "nodes/output_2.py": """\
from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import MergeBehavior


class Output2(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = ""

    class Trigger(FinalOutputNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES
""",
        "sandbox.py": """\
from vellum.workflows.inputs import DatasetRow

from .inputs import Inputs
from .nodes.code_execution import CodeExecution
from .nodes.code_execution_2 import CodeExecution2

dataset = [
    DatasetRow(
        label="With mocked code nodes",
        inputs=Inputs(json={}),
        node_output_mocks=[
            CodeExecution.Outputs(result="hello world", log=""),
            CodeExecution2.Outputs(result="hello world", log=""),
        ],
    ),
]
""",
        "workflow.py": """\
from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.code_execution import CodeExecution
from .nodes.code_execution_2 import CodeExecution2
from .nodes.output import Output
from .nodes.output_2 import Output2


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = {
        CodeExecution >> Output,
        CodeExecution2 >> Output2,
    }

    class Outputs(BaseWorkflow.Outputs):
        output = Output.Outputs.value
        output_2 = Output2.Outputs.value
""",
    }

    # AND a namespace for the virtual file loader
    namespace = str(uuid4())
    sys.meta_path.append(VirtualFileFinder(files, namespace))

    try:
        # WHEN we serialize the module
        result = BaseWorkflowDisplay.serialize_module(namespace)

        # THEN the serialization should return exactly 1 deprecation error
        assert len(result.errors) == 1, f"Expected 1 deprecation error, got {len(result.errors)}: {result.errors}"

        # AND the error should prompt the user to use 'mocks' instead of 'node_output_mocks'
        error_message = str(result.errors[0])
        assert "node_output_mocks" in error_message, f"Error should mention 'node_output_mocks': {error_message}"
        assert "mocks" in error_message, f"Error should mention 'mocks': {error_message}"
        assert "deprecated" in error_message.lower(), f"Error should mention 'deprecated': {error_message}"

        # AND the dataset should not be None (the deprecated field should still work)
        assert result.dataset is not None, "Dataset should not be None"

        # AND the dataset should have one row
        assert len(result.dataset) == 1, f"Dataset should have 1 row, got {len(result.dataset)}"

        # AND the row should have mocks serialized
        row = result.dataset[0]
        assert "mocks" in row, f"Row should have 'mocks' field, got keys: {row.keys()}"
        assert row["mocks"] is not None, "Mocks should not be None"
        assert len(row["mocks"]) == 2, f"Should have 2 mocks, got {len(row['mocks'])}"
    finally:
        # Clean up the virtual file finders
        sys.meta_path = [finder for finder in sys.meta_path if not isinstance(finder, VirtualFileFinder)]
