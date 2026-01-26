import pytest
from uuid import UUID
from typing import Optional

from vellum.client.types.chat_message import ChatMessage
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow, resolve_dataset_row
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs


def test_dataset_row_serialization():
    """
    Test that DatasetRow can be properly serialized to JSON and back.
    """

    class TestInputs(BaseInputs):
        message: str
        count: int
        optional_field: Optional[str] = None
        chat_history: list[ChatMessage]

    test_inputs = TestInputs(
        message="Hello World",
        count=42,
        optional_field="test",
        chat_history=[ChatMessage(text="Hello", role="USER"), ChatMessage(text="Hi there!", role="ASSISTANT")],
    )
    dataset_row = DatasetRow(label="test_label", inputs=test_inputs)

    serialized_dict = dataset_row.model_dump()

    assert "label" in serialized_dict
    assert "inputs" in serialized_dict
    assert serialized_dict["label"] == "test_label"

    inputs_data = serialized_dict["inputs"]
    assert inputs_data["message"] == "Hello World"
    assert inputs_data["count"] == 42
    assert inputs_data["optional_field"] == "test"
    assert "chat_history" in inputs_data
    assert len(inputs_data["chat_history"]) == 2
    assert inputs_data["chat_history"][0]["text"] == "Hello"
    assert inputs_data["chat_history"][0]["role"] == "USER"
    assert inputs_data["chat_history"][1]["text"] == "Hi there!"
    assert inputs_data["chat_history"][1]["role"] == "ASSISTANT"


def test_dataset_row_dict_serialization():
    """
    Test that DatasetRow can be properly converted to dict.
    """

    class SimpleInputs(BaseInputs):
        text: str

    simple_inputs = SimpleInputs(text="sample text")
    dataset_row = DatasetRow(label="simple_label", inputs=simple_inputs)

    result_dict = dataset_row.model_dump()

    assert result_dict["label"] == "simple_label"
    assert result_dict["inputs"]["text"] == "sample text"


def test_dataset_row_with_multiple_fields():
    """
    Test that DatasetRow works with BaseInputs that have multiple fields.
    """

    class MultiFieldInputs(BaseInputs):
        text_field: str
        number_field: int
        optional_field: Optional[str] = None

    multi_inputs = MultiFieldInputs(text_field="test_text", number_field=456, optional_field="optional_value")
    dataset_row = DatasetRow(label="multi_field_test", inputs=multi_inputs)

    result_dict = dataset_row.model_dump()

    assert result_dict["label"] == "multi_field_test"
    assert result_dict["inputs"]["text_field"] == "test_text"
    assert result_dict["inputs"]["number_field"] == 456
    assert result_dict["inputs"]["optional_field"] == "optional_value"


def test_dataset_row_with_default_inputs():
    """
    Test that DatasetRow works with BaseInputs that have default values.
    """

    class InputsWithDefaults(BaseInputs):
        required_field: str
        optional_with_default: str = "default_value"

    inputs_with_defaults = InputsWithDefaults(required_field="required_value")
    dataset_row = DatasetRow(label="defaults_test", inputs=inputs_with_defaults)

    serialized_dict = dataset_row.model_dump()

    assert serialized_dict["label"] == "defaults_test"
    assert serialized_dict["inputs"]["required_field"] == "required_value"
    assert serialized_dict["inputs"]["optional_with_default"] == "default_value"


def test_dataset_row_without_inputs():
    """
    Test that DatasetRow can be created with only a label (no inputs parameter).
    """

    dataset_row = DatasetRow(label="test_label_only")

    serialized_dict = dataset_row.model_dump()

    assert serialized_dict["label"] == "test_label_only"
    assert serialized_dict["inputs"] == {}

    assert isinstance(dataset_row.inputs, BaseInputs)


def test_dataset_row_with_empty_inputs():
    """
    Test that DatasetRow can be created with explicitly empty BaseInputs.
    """

    # GIVEN a DatasetRow with explicitly empty BaseInputs
    dataset_row = DatasetRow(label="test_label", inputs=BaseInputs())

    serialized_dict = dataset_row.model_dump()

    assert serialized_dict["label"] == "test_label"
    assert serialized_dict["inputs"] == {}


def test_dataset_row_with_dict_inputs():
    """
    Test that DatasetRow can accept a dict for the inputs parameter.
    """

    # GIVEN a dict with input data
    inputs_dict = {"message": "Hello World", "count": 42}

    dataset_row = DatasetRow(label="test_label", inputs=inputs_dict)

    # THEN the inputs should remain as a dict
    assert isinstance(dataset_row.inputs, dict)

    # AND the serialized dict should contain the correct data
    serialized_dict = dataset_row.model_dump()
    assert serialized_dict["label"] == "test_label"
    assert serialized_dict["inputs"]["message"] == "Hello World"
    assert serialized_dict["inputs"]["count"] == 42


def test_dataset_row_with_node_output_mocks():
    """
    Test that DatasetRow can be created with mocks and properly serialized.
    """

    # GIVEN a node with outputs
    class DummyNode(BaseNode):
        class Outputs(BaseOutputs):
            result: str

    # AND a DatasetRow with node output mocks
    mock_output = DummyNode.Outputs(result="mocked output")

    class TestInputs(BaseInputs):
        message: str

    test_inputs = TestInputs(message="test message")

    dataset_row = DatasetRow(label="test_with_mocks", inputs=test_inputs, mocks=[mock_output])

    serialized_dict = dataset_row.model_dump()

    # THEN the serialized dict should contain the label and inputs
    assert serialized_dict["label"] == "test_with_mocks"
    assert serialized_dict["inputs"]["message"] == "test message"

    # AND the mocks should be present in the serialized dict
    assert "mocks" in serialized_dict
    assert serialized_dict["mocks"] is not None
    assert len(serialized_dict["mocks"]) == 1

    # AND the mock output should be serialized as a dict with the correct structure
    mock_data = serialized_dict["mocks"][0]
    assert mock_data == {
        "type": "NODE_EXECUTION",
        "node_id": str(DummyNode.__id__),
        "when_condition": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": True}},
        "then_outputs": {"result": "mocked output"},
    }


def test_resolve_dataset_row__int_indexes_dataset_array():
    """
    Tests that an int selector indexes into the dataset array.
    """

    # GIVEN a dataset with multiple rows
    dataset = [
        DatasetRow(id="row-1", label="First Row", inputs={"message": "Hello"}),
        DatasetRow(id="row-2", label="Second Row", inputs={"message": "World"}),
        DatasetRow(id="row-3", label="Third Row", inputs={"message": "Test"}),
    ]

    # WHEN we resolve with an int selector
    result = resolve_dataset_row(dataset, 1)

    # THEN it should return the row at that index
    assert result.label == "Second Row"
    assert result.id == "row-2"


def test_resolve_dataset_row__string_matches_label():
    """
    Tests that a string selector matches the dataset row's label.
    """

    # GIVEN a dataset with multiple rows
    dataset = [
        DatasetRow(id="row-1", label="First Row", inputs={"message": "Hello"}),
        DatasetRow(id="row-2", label="Second Row", inputs={"message": "World"}),
        DatasetRow(id="row-3", label="Third Row", inputs={"message": "Test"}),
    ]

    # WHEN we resolve with a string selector matching a label
    result = resolve_dataset_row(dataset, "Second Row")

    # THEN it should return the row with that label
    assert result.label == "Second Row"
    assert result.id == "row-2"


def test_resolve_dataset_row__uuid_matches_id():
    """
    Tests that a UUID selector matches the dataset row's id.
    """

    # GIVEN a dataset with rows that have UUID-style ids
    row_uuid = UUID("12345678-1234-5678-1234-567812345678")
    dataset = [
        DatasetRow(id="row-1", label="First Row", inputs={"message": "Hello"}),
        DatasetRow(id=str(row_uuid), label="Second Row", inputs={"message": "World"}),
        DatasetRow(id="row-3", label="Third Row", inputs={"message": "Test"}),
    ]

    # WHEN we resolve with a UUID selector
    result = resolve_dataset_row(dataset, row_uuid)

    # THEN it should return the row with that id
    assert result.label == "Second Row"
    assert result.id == str(row_uuid)


def test_resolve_dataset_row__int_out_of_bounds_raises_index_error():
    """
    Tests that an int selector out of bounds raises IndexError.
    """

    # GIVEN a dataset with 2 rows
    dataset = [
        DatasetRow(label="First Row", inputs={"message": "Hello"}),
        DatasetRow(label="Second Row", inputs={"message": "World"}),
    ]

    # WHEN we resolve with an out-of-bounds index
    # THEN it should raise IndexError
    with pytest.raises(IndexError, match="out of bounds"):
        resolve_dataset_row(dataset, 5)


def test_resolve_dataset_row__string_not_found_raises_value_error():
    """
    Tests that a string selector that doesn't match any label raises ValueError.
    """

    # GIVEN a dataset with rows
    dataset = [
        DatasetRow(label="First Row", inputs={"message": "Hello"}),
        DatasetRow(label="Second Row", inputs={"message": "World"}),
    ]

    # WHEN we resolve with a non-existent label
    # THEN it should raise ValueError
    with pytest.raises(ValueError, match="No dataset row found with label"):
        resolve_dataset_row(dataset, "Non-existent Row")


def test_resolve_dataset_row__uuid_not_found_raises_value_error():
    """
    Tests that a UUID selector that doesn't match any id raises ValueError.
    """

    # GIVEN a dataset with rows
    dataset = [
        DatasetRow(id="row-1", label="First Row", inputs={"message": "Hello"}),
        DatasetRow(id="row-2", label="Second Row", inputs={"message": "World"}),
    ]

    # WHEN we resolve with a non-existent UUID
    non_existent_uuid = UUID("99999999-9999-9999-9999-999999999999")

    # THEN it should raise ValueError
    with pytest.raises(ValueError, match="No dataset row found with id"):
        resolve_dataset_row(dataset, non_existent_uuid)


def test_resolve_dataset_row__base_inputs_converted_to_dataset_row():
    """
    Tests that BaseInputs in the dataset are converted to DatasetRow when resolved by int.
    """

    # GIVEN a dataset with BaseInputs (not DatasetRow)
    class TestInputs(BaseInputs):
        message: str

    dataset = [
        TestInputs(message="Hello"),
        TestInputs(message="World"),
    ]

    # WHEN we resolve with an int selector
    result = resolve_dataset_row(dataset, 0)

    # THEN it should return a DatasetRow with a default label
    assert isinstance(result, DatasetRow)
    assert result.label == "Scenario 1"
    assert result.inputs.message == "Hello"
