import pytest
from typing import Optional

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
    assert "Required input variables required_string should have defined value" == str(exc_info.value)


def test_base_inputs_with_default():
    # GIVEN some input class with a field that has a default value
    class TestInputs(BaseInputs):
        string_with_default: str = "default_value"

    # WHEN we create an instance without providing the field
    inputs = TestInputs()

    # THEN it should use the default value
    assert inputs.string_with_default == "default_value"
