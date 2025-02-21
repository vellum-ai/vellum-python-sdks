import pytest
from typing import Optional

from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
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

    # WHEN we try to assign None to a required field
    with pytest.raises(NodeException) as exc_info:
        TestInputs(required_string=None, optional_string="ok")

    # THEN it should raise a NodeException with the correct error message and code
    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Required input variables should have defined value" in str(exc_info.value)


def test_base_inputs_empty_string():
    # GIVEN some input class with required and optional string fields
    class TestInputs(BaseInputs):
        required_string: str
        optional_string: Optional[str]

    # WHEN we try to assign an empty string to a required string field
    with pytest.raises(NodeException) as exc_info:
        TestInputs(required_string="", optional_string="ok")

    # THEN it should raise a NodeException with the correct error message and code
    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS
    assert "Empty string not allowed for required string input" in str(exc_info.value)
