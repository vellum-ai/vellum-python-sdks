import pytest
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
from uuid import UUID

from pytest_mock import MockerFixture

from vellum.workflows.exceptions import WorkflowInitializationException
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder

from tests.workflows.test_node_output_mock_when_conditions.workflow import ProcessNode


@pytest.fixture
def temp_module_path():
    """Fixture to manage sys.path for temporary modules."""
    temp_dir = tempfile.mkdtemp()
    sys.path.insert(0, temp_dir)
    try:
        yield temp_dir
    finally:
        sys.path.remove(temp_dir)
        shutil.rmtree(temp_dir)


@pytest.fixture
def metadata_trigger_factory(mocker: MockerFixture):
    def _factory(metadata_trigger_id: UUID) -> UUID:
        mocker.patch(
            "vellum.workflows.triggers.base._get_trigger_id_from_metadata",
            return_value=metadata_trigger_id,
        )
        return metadata_trigger_id

    return _factory


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


def test_serialize_module_with_actual_dataset_with_scheduled_trigger(metadata_trigger_factory):
    """Test that serialize_module correctly serializes dataset with trigger"""
    module_path = "tests.workflows.test_dataset_with_trigger_serialization"

    metadata_trigger_id = uuid.uuid4()
    metadata_trigger_factory(metadata_trigger_id)

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "dataset")

    assert result.dataset is not None
    assert isinstance(result.dataset, list)
    assert len(result.dataset) == 1

    assert result.dataset[0]["label"] == "Scenario 1"
    assert result.dataset[0]["workflow_trigger_id"] == str(metadata_trigger_id)

    inputs = result.dataset[0]["inputs"]
    assert len(inputs) == 2

    assert "current_run_at" in inputs
    assert "next_run_at" in inputs


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


def test_serialize_module__includes_runner_config():
    """
    Tests that serialize_module includes runner_config in exec_config.
    """
    # GIVEN a valid module path without metadata.json runner_config
    module_path = "tests.workflows.trivial"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module_path)

    # THEN the exec_config should contain runner_config
    assert "runner_config" in result.exec_config

    # AND runner_config should be an empty dict when no metadata.json runner_config exists
    runner_config = result.exec_config["runner_config"]
    assert isinstance(runner_config, dict)


def test_serialize_module__runner_config_from_metadata():
    """
    Tests that serialize_module reads runner_config from metadata.json.
    """
    # GIVEN a module path with metadata.json containing runner_config
    module_path = "ee.vellum_ee.workflows.tests.local_workflow"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module_path)

    # THEN the exec_config should contain runner_config
    assert "runner_config" in result.exec_config

    # AND runner_config should be a dict (loaded from metadata.json)
    runner_config = result.exec_config["runner_config"]
    assert isinstance(runner_config, dict)


def test_serialize_module_includes_additional_files():
    """
    Tests that serialize_module includes only Python files from the module directory.

    Non-Python files (like .txt) should be excluded from additional_files.
    """
    # GIVEN a module path with additional files including both .py and non-.py files
    module_path = "tests.workflows.module_with_additional_files"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module_path)

    # THEN the result should have the expected structure
    assert hasattr(result, "exec_config")
    assert hasattr(result, "errors")
    assert isinstance(result.exec_config, dict)
    assert isinstance(result.errors, list)

    # AND module_data should contain additional_files
    assert "module_data" in result.exec_config
    assert "additional_files" in result.exec_config["module_data"]

    additional_files = result.exec_config["module_data"]["additional_files"]
    assert isinstance(additional_files, dict)

    # AND Python helper files should be included
    assert "helper.py" in additional_files
    assert "utils/constants.py" in additional_files
    assert "utils/__init__.py" in additional_files

    # AND non-Python files should NOT be included
    assert "data.txt" not in additional_files

    # AND serialized workflow files should NOT be included
    assert "workflow.py" not in additional_files
    assert "__init__.py" not in additional_files
    assert "nodes/test_node.py" not in additional_files

    # AND the Python file contents should be correct
    assert "def helper_function():" in additional_files["helper.py"]
    assert "CONSTANT_VALUE" in additional_files["utils/constants.py"]


def test_serialize_module_with_pydantic_array():
    """
    Test that serialize_module correctly serializes arrays of Pydantic models in workflow inputs.

    This test verifies that when a workflow has inputs containing a List[PydanticModel],
    the serialization properly converts the Pydantic models to JSON format.
    """
    module_path = "tests.workflows.pydantic_array_serialization"

    # WHEN we serialize it
    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "exec_config")
    assert hasattr(result, "errors")
    assert isinstance(result.exec_config, dict)
    assert isinstance(result.errors, list)

    input_variables = result.exec_config["input_variables"]
    assert len(input_variables) == 1

    items_input = input_variables[0]
    assert items_input["key"] == "items"
    assert items_input["type"] == "JSON"
    # The schema field now includes the OpenAPI spec for the input type
    assert items_input["schema"] == {
        "type": "array",
        "items": {"$ref": "#/$defs/tests.workflows.pydantic_array_serialization.workflow.CustomItem"},
    }

    assert result.dataset is not None
    assert isinstance(result.dataset, list)
    assert len(result.dataset) == 2

    first_scenario = result.dataset[0]
    assert first_scenario["label"] == "Scenario 1"
    assert "items" in first_scenario["inputs"]
    items = first_scenario["inputs"]["items"]
    assert isinstance(items, list)
    assert len(items) == 3
    assert items[0]["name"] == "item1"
    assert items[0]["value"] == 10
    assert items[0]["is_active"] is True

    second_scenario = result.dataset[1]
    assert second_scenario["label"] == "Custom Test"
    assert "items" in second_scenario["inputs"]
    test_items = second_scenario["inputs"]["items"]
    assert len(test_items) == 2
    assert test_items[0]["name"] == "test1"
    assert test_items[0]["value"] == 100


def test_serialize_module_with_dataset_row_id_from_metadata():
    """
    Tests that serialize_module correctly reads dataset row IDs from metadata.json.

    Verifies that IDs are included in the serialized dataset.
    """
    module_path = "tests.workflows.test_dataset_row_id_serialization"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "dataset")
    assert result.dataset is not None
    assert isinstance(result.dataset, list)
    assert len(result.dataset) == 3

    assert result.dataset[0]["label"] == "Scenario 1"
    assert result.dataset[0]["inputs"]["message"] == "World"
    assert result.dataset[0]["id"] == "dataset-row-id-1"

    assert result.dataset[1]["label"] == "Scenario 2"
    assert result.dataset[1]["inputs"]["message"] == "Test"
    assert result.dataset[1]["id"] == "dataset-row-id-2"

    assert result.dataset[2]["label"] == "Scenario 3 without ID"
    assert result.dataset[2]["inputs"]["message"] == "No ID"
    # AND the third row should have a deterministic hash-based ID since it has no explicit ID
    assert result.dataset[2]["id"] == "cc40aa9b-179a-43fc-8fda-d40ea8a8e300"


def test_serialize_module_with_base_inputs_and_metadata():
    """
    Tests that BaseInputs rows get IDs from metadata.json mapping.

    Verifies round-trip preservation for workflows using plain BaseInputs entries.
    """
    module_path = "tests.workflows.test_base_inputs_with_metadata"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "dataset")
    assert result.dataset is not None
    assert isinstance(result.dataset, list)
    assert len(result.dataset) == 2

    assert result.dataset[0]["label"] == "Scenario 1"
    assert result.dataset[0]["inputs"]["message"] == "World"
    assert result.dataset[0]["id"] == "base-inputs-id-1"

    assert result.dataset[1]["label"] == "Scenario 2"
    assert result.dataset[1]["inputs"]["message"] == "Test"
    assert result.dataset[1]["id"] == "base-inputs-id-2"


def test_serialize_module_with_node_output_mock_when_conditions():
    """
    Tests that serialize_module correctly serializes node output mocks with when conditions.

    Verifies that when conditions involving workflow inputs and node execution counters
    are properly serialized in the dataset.
    """
    module_path = "tests.workflows.test_node_output_mock_when_conditions"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert hasattr(result, "dataset")
    assert result.dataset is not None
    assert isinstance(result.dataset, list)
    assert len(result.dataset) == 2

    first_scenario = result.dataset[0]
    assert first_scenario["label"] == "Scenario 1"
    assert first_scenario["inputs"]["threshold"] == 5

    assert "mocks" in first_scenario
    assert isinstance(first_scenario["mocks"], list)
    assert len(first_scenario["mocks"]) == 2

    first_mock = first_scenario["mocks"][0]
    workflow_input_id = first_mock["when_condition"]["lhs"]["lhs"]["input_variable_id"]
    node_id = str(ProcessNode.__id__)

    assert first_mock == {
        "type": "NODE_EXECUTION",
        "node_id": node_id,
        "when_condition": {
            "type": "BINARY_EXPRESSION",
            "lhs": {
                "type": "BINARY_EXPRESSION",
                "lhs": {"type": "WORKFLOW_INPUT", "input_variable_id": workflow_input_id},
                "operator": "=",
                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 5.0}},
            },
            "operator": "and",
            "rhs": {
                "type": "BINARY_EXPRESSION",
                "lhs": {"type": "EXECUTION_COUNTER", "node_id": node_id},
                "operator": "=",
                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 0.0}},
            },
        },
        "then_outputs": {"result": "first_execution_threshold_5"},
    }

    second_mock = first_scenario["mocks"][1]
    assert second_mock == {
        "type": "NODE_EXECUTION",
        "node_id": node_id,
        "when_condition": {
            "type": "BINARY_EXPRESSION",
            "lhs": {
                "type": "BINARY_EXPRESSION",
                "lhs": {"type": "WORKFLOW_INPUT", "input_variable_id": workflow_input_id},
                "operator": "=",
                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 5.0}},
            },
            "operator": "and",
            "rhs": {
                "type": "BINARY_EXPRESSION",
                "lhs": {"type": "EXECUTION_COUNTER", "node_id": node_id},
                "operator": "=",
                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 1.0}},
            },
        },
        "then_outputs": {"result": "second_execution_threshold_5"},
    }

    second_scenario = result.dataset[1]
    assert second_scenario["label"] == "Scenario 2"
    assert second_scenario["inputs"]["threshold"] == 10

    assert "mocks" in second_scenario
    assert isinstance(second_scenario["mocks"], list)
    assert len(second_scenario["mocks"]) == 1

    third_mock = second_scenario["mocks"][0]
    assert third_mock == {
        "type": "NODE_EXECUTION",
        "node_id": node_id,
        "when_condition": {
            "type": "BINARY_EXPRESSION",
            "lhs": {
                "type": "BINARY_EXPRESSION",
                "lhs": {"type": "WORKFLOW_INPUT", "input_variable_id": workflow_input_id},
                "operator": "=",
                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 10.0}},
            },
            "operator": "and",
            "rhs": {
                "type": "BINARY_EXPRESSION",
                "lhs": {"type": "EXECUTION_COUNTER", "node_id": node_id},
                "operator": "=",
                "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 0.0}},
            },
        },
        "then_outputs": {"result": "first_execution_threshold_10"},
    }


def test_serialize_module__with_invalid_nested_set_graph(temp_module_path):
    """
    Tests that serialize_module raises a clear user-facing exception for workflows with nested sets in graph attribute.
    """
    module_dir = Path(temp_module_path) / "test_invalid_workflow"
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

    with pytest.raises(WorkflowInitializationException) as exc_info:
        BaseWorkflowDisplay.serialize_module("test_invalid_workflow")

    error_message = str(exc_info.value)
    assert "Invalid graph structure detected" in error_message
    assert "Nested sets or unsupported graph types are not allowed" in error_message
    assert "contact Vellum support" in error_message


def test_serialize_module__with_invalid_parent_node_output_reference():
    """
    Tests that serialize_module surfaces an error for workflows with nodes
    that reference their parent class's outputs.
    """
    module_path = "tests.workflows.invalid_parent_node_output_reference"

    result = BaseWorkflowDisplay.serialize_module(module_path)

    assert len(result.errors) == 1
    assert result.errors[0].message == (
        "'ReportGeneratorNode.Outputs.report_content' references parent class output 'InlinePromptNode.Outputs.text'. "
        "Referencing outputs from a node's parent class is not allowed."
        "\n"
        "'ReportGeneratorNode.Outputs.report_json' references parent class output 'InlinePromptNode.Outputs.json'. "
        "Referencing outputs from a node's parent class is not allowed."
    )


def test_serialize_module__virtual_files_include_integration_models():
    """
    Tests that serialize_module includes integration_models files in additional_files
    when the workflow is loaded from virtual files.
    """
    # GIVEN a workflow loaded from virtual files with integration_models directory
    files = {
        "__init__.py": "",
        "inputs.py": """from vellum.workflows.inputs import BaseInputs

class Inputs(BaseInputs):
    channel_id: str = "C0123456789"
""",
        "workflow.py": """from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.test_node import TestNode


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = TestNode

    class Outputs(BaseWorkflow.Outputs):
        result = TestNode.Outputs.result
""",
        "nodes/__init__.py": "",
        "nodes/test_node.py": """from vellum.workflows.nodes.bases import BaseNode

from ..inputs import Inputs
from ..integration_models.slack_input import SlackInput


class TestNode(BaseNode):
    channel_id = Inputs.channel_id

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        request = SlackInput(channel=self.channel_id)
        return self.Outputs(result=request.channel)
""",
        "integration_models/__init__.py": "",
        "integration_models/slack_input.py": """from pydantic import BaseModel


class SlackInput(BaseModel):
    channel: str
""",
        "integration_models/slack_output.py": """from pydantic import BaseModel


class SlackOutput(BaseModel):
    messages: list
""",
    }

    namespace = str(uuid.uuid4())
    finder = VirtualFileFinder(files, namespace)
    sys.meta_path.insert(0, finder)

    try:
        # WHEN we serialize the module
        result = BaseWorkflowDisplay.serialize_module(namespace)

        # THEN the result should have module_data with additional_files
        assert "module_data" in result.exec_config
        assert "additional_files" in result.exec_config["module_data"]

        additional_files = result.exec_config["module_data"]["additional_files"]

        # AND integration_models files should be included
        assert "integration_models/__init__.py" in additional_files
        assert "integration_models/slack_input.py" in additional_files
        assert "integration_models/slack_output.py" in additional_files

        # AND the file contents should be correct
        assert "class SlackInput" in additional_files["integration_models/slack_input.py"]
        assert "class SlackOutput" in additional_files["integration_models/slack_output.py"]

        # AND serialized workflow files should NOT be included
        assert "workflow.py" not in additional_files
        assert "__init__.py" not in additional_files
        assert "nodes/test_node.py" not in additional_files
    finally:
        sys.meta_path.remove(finder)
