from typing import Optional

from vellum.client.types.chat_message import ChatMessage
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.inputs.dataset_row import DatasetRow


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
