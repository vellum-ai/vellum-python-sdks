import json
from typing import Optional

from vellum.workflows.dataset_row import DatasetRow
from vellum.workflows.inputs.base import BaseInputs


def test_dataset_row_serialization():
    """
    Test that DatasetRow can be properly serialized to JSON and back.
    """

    class TestInputs(BaseInputs):
        message: str
        count: int
        optional_field: Optional[str] = None

    test_inputs = TestInputs(message="Hello World", count=42, optional_field="test")
    dataset_row = DatasetRow(label="test_label", inputs=test_inputs)

    serialized_json = dataset_row.json()
    serialized_dict = json.loads(serialized_json)

    assert "label" in serialized_dict
    assert "inputs" in serialized_dict
    assert serialized_dict["label"] == "test_label"

    inputs_data = serialized_dict["inputs"]
    assert inputs_data["message"] == "Hello World"
    assert inputs_data["count"] == 42
    assert inputs_data["optional_field"] == "test"


def test_dataset_row_dict_serialization():
    """
    Test that DatasetRow can be properly converted to dict.
    """

    class SimpleInputs(BaseInputs):
        text: str

    simple_inputs = SimpleInputs(text="sample text")
    dataset_row = DatasetRow(label="simple_label", inputs=simple_inputs)

    result_dict = dataset_row.dict()

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

    result_dict = dataset_row.dict()

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

    serialized_json = dataset_row.json()
    serialized_dict = json.loads(serialized_json)

    assert serialized_dict["label"] == "defaults_test"
    assert serialized_dict["inputs"]["required_field"] == "required_value"
    assert serialized_dict["inputs"]["optional_with_default"] == "default_value"
