import pytest
from typing import Any, Optional

from pydantic import Field

from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.inputs import BaseInputs


def test_base_inputs_happy_path():
    # GIVEN some input class with required and optional fields
    class TestInputs(BaseInputs):
        required_string: str
        required_int: int
        optional_string: Optional[str]

    # WHEN we assign the inputs some valid values
    inputs = TestInputs(required_string="hello", required_int=42, optional_string=None)

    # THEN the inputs should have the correct values
    assert inputs.required_string == "hello"
    assert inputs.required_int == 42
    assert inputs.optional_string is None


def test_base_inputs_explicit_none():
    """
    Test that None can be explicitly set as a value, distinguishing it from not providing a value.
    """

    # GIVEN some input class with optional fields and fields with defaults
    class TestInputs(BaseInputs):
        optional_string: Optional[str]
        optional_string_with_default: Optional[str] = None

    # WHEN we explicitly pass None for optional fields
    inputs = TestInputs(optional_string=None)

    assert inputs.optional_string is None
    assert inputs.optional_string_with_default is None


@pytest.mark.parametrize("field_type", [str, Optional[str]])
def test_base_inputs_explicit_none_should_raise_on_fields_without_defaults(field_type):
    """
    Test that None cannot be explicitly set as a value for required fields.
    """

    class TestInputs(BaseInputs):
        required_string: field_type  # type: ignore[valid-type]

    with pytest.raises(WorkflowInitializationException) as exc_info:
        TestInputs()  # type: ignore[call-arg]

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Required input variables 'required_string' should have defined value" == str(exc_info.value)


def test_base_inputs_explicit_none_should_raise_on_required_fields_with_none():
    """
    Test that None cannot be explicitly set as a value for required fields.
    """

    class TestInputs(BaseInputs):
        required_string: str

    with pytest.raises(WorkflowInitializationException) as exc_info:
        TestInputs(required_string=None)  # type: ignore[arg-type]

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Required input variables 'required_string' should have defined value" == str(exc_info.value)


def test_base_inputs_empty_value():
    # GIVEN some input class with required and optional string fields
    class TestInputs(BaseInputs):
        required_string: str
        optional_string: Optional[str]

    # WHEN we try to omit a required field
    with pytest.raises(WorkflowInitializationException) as exc_info:
        TestInputs(optional_string="ok")  # type: ignore

    # THEN it should raise a NodeException with the correct error message and code
    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Required input variables 'required_string' should have defined value" == str(exc_info.value)


def test_base_inputs_with_default():
    # GIVEN some input class with a field that has a default value
    class TestInputs(BaseInputs):
        string_with_default: str = "default_value"

    # WHEN we create an instance without providing the field
    inputs = TestInputs()

    # THEN it should use the default value
    assert inputs.string_with_default == "default_value"


def test_base_inputs_with_field_default_factory_empty_list():
    """
    Test that Field(default_factory=list) works correctly for JSON array inputs.
    This ensures that each instance gets a separate list instance, avoiding mutable default issues.
    """

    # GIVEN some input class with Field(default_factory=list) for JSON array
    class TestInputs(BaseInputs):
        json_array_input: Any = Field(default_factory=list)  # type: ignore[arg-type]
        array_input: list[str] = Field(default_factory=list)  # type: ignore[arg-type]

    # WHEN we create two instances without providing values
    inputs1 = TestInputs()
    inputs2 = TestInputs()

    # THEN they should get separate list instances
    assert inputs1.json_array_input is not inputs2.json_array_input
    assert isinstance(inputs1.json_array_input, list)
    assert isinstance(inputs2.json_array_input, list)

    # WHEN we modify one instance
    inputs1.json_array_input.append("test1")
    inputs2.json_array_input.append("test2")

    # THEN the other instance should be unaffected
    assert inputs1.json_array_input == ["test1"]
    assert inputs2.json_array_input == ["test2"]


def test_base_inputs_with_field_default_factory_non_empty_list():
    """
    Test that Field(default_factory=list) works correctly for non-empty list inputs.
    """

    # GIVEN some input class with Field(default_factory=list) for non-empty list
    class TestInputs(BaseInputs):
        non_empty_list_input: list[str] = Field(default_factory=lambda: ["test1", "test2"])

    # WHEN we create an instance without providing values
    inputs1 = TestInputs()
    inputs2 = TestInputs()

    # THEN it should use the default value
    assert inputs1.non_empty_list_input == ["test1", "test2"]
    assert inputs2.non_empty_list_input == ["test1", "test2"]

    # WHEN we modify one instance
    inputs1.non_empty_list_input.append("test3")
    inputs2.non_empty_list_input.append("test4")

    # THEN the other instance should be unaffected
    assert inputs1.non_empty_list_input == ["test1", "test2", "test3"]
    assert inputs2.non_empty_list_input == ["test1", "test2", "test4"]


def test_base_inputs_with_field_default_factory_empty_dict():
    """
    Test that Field(default_factory=dict) works correctly for JSON dict inputs.
    This ensures that each instance gets a separate dict instance, avoiding mutable default issues.
    """

    # GIVEN some input class with Field(default_factory=dict) for JSON dict
    class TestInputs(BaseInputs):
        json_dict_input: Any = Field(default_factory=dict)  # type: ignore[arg-type]

    # WHEN we create two instances without providing values
    inputs1 = TestInputs()
    inputs2 = TestInputs()

    # THEN they should get separate dict instances
    assert inputs1.json_dict_input is not inputs2.json_dict_input
    assert isinstance(inputs1.json_dict_input, dict)
    assert isinstance(inputs2.json_dict_input, dict)

    # WHEN we modify one instance
    inputs1.json_dict_input["key1"] = "value1"
    inputs2.json_dict_input["key2"] = "value2"

    # THEN the other instance should be unaffected
    assert inputs1.json_dict_input == {"key1": "value1"}
    assert inputs2.json_dict_input == {"key2": "value2"}


def test_base_inputs_with_field_default_factory_non_empty_dict():
    """
    Test that Field(default_factory=dict) works correctly for non-empty dict inputs.
    """

    # GIVEN some input class with Field(default_factory=dict) for non-empty dict
    class TestInputs(BaseInputs):
        non_empty_dict_input: dict[str, str] = Field(default_factory=lambda: {"key1": "value1", "key2": "value2"})

    # WHEN we create an instance without providing values
    inputs1 = TestInputs()
    inputs2 = TestInputs()

    # THEN it should use the default value
    assert inputs1.non_empty_dict_input == {"key1": "value1", "key2": "value2"}
    assert inputs2.non_empty_dict_input == {"key1": "value1", "key2": "value2"}

    # WHEN we modify one instance
    inputs1.non_empty_dict_input["key3"] = "value3"
    inputs2.non_empty_dict_input["key4"] = "value4"

    # THEN the other instance should be unaffected
    assert inputs1.non_empty_dict_input == {"key1": "value1", "key2": "value2", "key3": "value3"}
    assert inputs2.non_empty_dict_input == {"key1": "value1", "key2": "value2", "key4": "value4"}


def test_base_inputs__supports_inherited_inputs():
    # GIVEN an inputs class
    class TopInputs(BaseInputs):
        first: str

    # WHEN we inherit from the base inputs class
    class BottomInputs(TopInputs):
        second: int

    # THEN both references should be available
    assert BottomInputs.first.name == "first"
    assert BottomInputs.second.name == "second"
    assert len([ref for ref in BottomInputs]) == 2


def test_base_inputs__iterating_over_descriptor_is_finite():
    """
    Tests that iterating over a descriptor (like Inputs.image_url) creates a finite generator.
    This was the bug reported in Slack where AB sometimes generates code that iterates over descriptors.
    """

    class Inputs(BaseInputs):
        image_url: str

    iteration_count = 0
    try:
        for idx, x in enumerate(Inputs.image_url):  # type: ignore[arg-type,var-annotated]
            iteration_count += 1
            if idx > 100:
                break
    except (TypeError, IndexError):
        pass

    assert iteration_count < 100
