import pytest
from pathlib import Path
import sys
import tempfile

from vellum.workflows.exceptions import WorkflowInitializationException
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module_with_dataset():
    """Test that serialize_module correctly serializes dataset from sandbox modules."""
    module_path = "tests.workflows.basic_inputs_and_outputs"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "dataset")

    assert result.dataset is None


def test_serialize_module_with_actual_dataset():
    """Test that serialize_module correctly serializes dataset when sandbox has dataset attribute."""
    module_path = "tests.workflows.test_dataset_serialization"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "dataset")

    assert result.dataset is not None
    assert isinstance(result.dataset, list)
    assert len(result.dataset) == 2

    assert result.dataset[0]["label"] == "Scenario 1"
    assert result.dataset[0]["inputs"]["message"] == "World"

    assert result.dataset[1]["label"] == "Custom Test"
    assert result.dataset[1]["inputs"]["message"] == "DatasetRow Test"


def test_serialize_module_happy_path():
    """Test that serialize_module works with a valid module path."""
    module_path = "tests.workflows.trivial"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "exec_config")
    assert hasattr(result, "errors")
    assert isinstance(result.exec_config, dict)
    assert isinstance(result.errors, list)
    assert "workflow_raw_data" in result.exec_config
    assert "input_variables" in result.exec_config
    assert "output_variables" in result.exec_config


def test_serialize_module_includes_additional_files():
    """Test that serialize_module includes additional files from the module directory."""
    module_path = "tests.workflows.module_with_additional_files"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "exec_config")
    assert hasattr(result, "errors")
    assert isinstance(result.exec_config, dict)
    assert isinstance(result.errors, list)

    assert "module_data" in result.exec_config
    assert "additional_files" in result.exec_config["module_data"]

    additional_files = result.exec_config["module_data"]["additional_files"]
    assert isinstance(additional_files, dict)

    assert "helper.py" in additional_files
    assert "data.txt" in additional_files
    assert "utils/constants.py" in additional_files

    assert "workflow.py" not in additional_files
    assert "__init__.py" not in additional_files
    assert "utils/__init__.py" in additional_files
    assert "nodes/test_node.py" not in additional_files

    assert "def helper_function():" in additional_files["helper.py"]
    assert "sample data file" in additional_files["data.txt"]
    assert "CONSTANT_VALUE" in additional_files["utils/constants.py"]


def test_serialize_module__with_invalid_nested_set_graph():
    """
    Tests that serialize_module raises a clear user-facing exception for workflows with nested sets in graph attribute.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        module_dir = Path(temp_dir) / "test_invalid_workflow"
        module_dir.mkdir()

        (module_dir / "__init__.py").write_text("")

        workflow_content = """
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode

class TestNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value = "test"

class InvalidWorkflow(BaseWorkflow):
    graph = {TestNode, {TestNode}}

    class Outputs(BaseWorkflow.Outputs):
        result = TestNode.Outputs.value
"""
        (module_dir / "workflow.py").write_text(workflow_content)

        sys.path.insert(0, temp_dir)

        try:
            with pytest.raises(WorkflowInitializationException) as exc_info:
                BaseWorkflowDisplay.serialize_module("test_invalid_workflow")

            error_message = str(exc_info.value)
            assert "Invalid graph structure detected" in error_message
            assert "Nested sets or unsupported graph types are not allowed" in error_message
            assert "contact Vellum support" in error_message
        finally:
            sys.path.remove(temp_dir)
