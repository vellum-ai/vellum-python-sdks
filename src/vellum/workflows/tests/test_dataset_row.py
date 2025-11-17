from typing import Optional

from vellum.client.types.chat_message import ChatMessage
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow
from vellum.workflows.nodes.mocks import MockNodeExecution
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.constant import ConstantValueReference


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


def test_dataset_row_with_node_output_mocks__base_outputs():
    """
    Tests that DatasetRow can accept node_output_mocks with BaseOutputs instances.
    """

    # GIVEN a simple inputs class
    class SimpleInputs(BaseInputs):
        text: str

    class SimpleOutputs(BaseOutputs):
        result: str

    mock_outputs = SimpleOutputs(result="mocked_result")

    dataset_row = DatasetRow(
        label="test_with_mocks",
        inputs=SimpleInputs(text="test"),
        node_output_mocks=[mock_outputs],
    )

    # THEN the node_output_mocks should be stored correctly
    assert dataset_row.node_output_mocks is not None
    assert len(dataset_row.node_output_mocks) == 1
    assert isinstance(dataset_row.node_output_mocks[0], BaseOutputs)
    assert isinstance(dataset_row.node_output_mocks[0], SimpleOutputs)
    assert dataset_row.node_output_mocks[0].result == "mocked_result"

    # AND the serialized dict should contain the node_output_mocks
    serialized_dict = dataset_row.model_dump()
    assert "node_output_mocks" in serialized_dict
    assert serialized_dict["node_output_mocks"] is not None


def test_dataset_row_with_node_output_mocks__mock_node_execution():
    """
    Tests that DatasetRow can accept node_output_mocks with MockNodeExecution instances.
    """

    # GIVEN a simple outputs class
    class SimpleOutputs(BaseOutputs):
        result: str

    mock_execution = MockNodeExecution(
        when_condition=ConstantValueReference(True),
        then_outputs=SimpleOutputs(result="mocked_result"),
    )

    dataset_row = DatasetRow(
        label="test_with_mock_execution",
        inputs={"text": "test"},
        node_output_mocks=[mock_execution],
    )

    # THEN the node_output_mocks should be stored correctly
    assert dataset_row.node_output_mocks is not None
    assert len(dataset_row.node_output_mocks) == 1
    assert isinstance(dataset_row.node_output_mocks[0], MockNodeExecution)
    mock_exec = dataset_row.node_output_mocks[0]
    assert isinstance(mock_exec.then_outputs, SimpleOutputs)
    assert mock_exec.then_outputs.result == "mocked_result"

    # AND the serialized dict should contain the node_output_mocks
    serialized_dict = dataset_row.model_dump()
    assert "node_output_mocks" in serialized_dict
    assert serialized_dict["node_output_mocks"] is not None


def test_dataset_row_with_node_output_mocks__none():
    """
    Tests that DatasetRow node_output_mocks can be None (optional).
    """

    # GIVEN a DatasetRow without node_output_mocks specified
    dataset_row = DatasetRow(label="test_without_mocks", inputs={"text": "test"})

    # THEN the node_output_mocks should be None
    assert dataset_row.node_output_mocks is None

    # AND the serialized dict should contain node_output_mocks as None
    serialized_dict = dataset_row.model_dump()
    assert "node_output_mocks" in serialized_dict
    assert serialized_dict["node_output_mocks"] is None


def test_dataset_row_with_node_output_mocks__mixed_types():
    """
    Tests that DatasetRow can accept node_output_mocks with mixed BaseOutputs and MockNodeExecution.
    """

    # GIVEN a simple outputs class
    class SimpleOutputs(BaseOutputs):
        result: str

    mock_outputs = SimpleOutputs(result="direct_mock")

    mock_execution = MockNodeExecution(
        when_condition=ConstantValueReference(True),
        then_outputs=SimpleOutputs(result="conditional_mock"),
    )

    dataset_row = DatasetRow(
        label="test_with_mixed_mocks",
        inputs={"text": "test"},
        node_output_mocks=[mock_outputs, mock_execution],
    )

    assert dataset_row.node_output_mocks is not None
    assert len(dataset_row.node_output_mocks) == 2
    assert isinstance(dataset_row.node_output_mocks[0], BaseOutputs)
    assert isinstance(dataset_row.node_output_mocks[1], MockNodeExecution)

    # AND the serialized dict should contain both mocks
    serialized_dict = dataset_row.model_dump()
    assert "node_output_mocks" in serialized_dict
    assert len(serialized_dict["node_output_mocks"]) == 2
