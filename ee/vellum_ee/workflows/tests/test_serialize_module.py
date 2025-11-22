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


def test_serialize_module_with_actual_dataset_with_trigger(metadata_trigger_factory):
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
    assert items_input["type"] == "ARRAY"
    # TODO: Add support for pydantic models
    assert "schema" not in items_input

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
    assert "id" not in result.dataset[2]


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
