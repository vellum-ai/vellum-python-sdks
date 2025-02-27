import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


def test_parse_json_success():
    # Test successful JSON parsing
    state = BaseState()
    expression = ConstantValueReference('{"key": "value"}').parse_json()
    result = expression.resolve(state)

    assert result == {"key": "value"}


def test_parse_json_array():
    # Test parsing a JSON array
    state = BaseState()
    expression = ConstantValueReference("[1, 2, 3]").parse_json()

    # This should raise an exception because we've defined types=(dict,)
    with pytest.raises(InvalidExpressionException) as exc_info:
        expression.resolve(state)

    # Verify the error message mentions the expected type
    assert "Expected JSON to parse to a dictionary, but got list" == str(exc_info.value)


def test_parse_json_invalid_json():
    # Test with invalid JSON
    state = BaseState()
    expression = ConstantValueReference('{"key": value}').parse_json()

    with pytest.raises(InvalidExpressionException) as exc_info:
        expression.resolve(state)

    # Verify the error message indicates JSON parsing failure
    assert 'Failed to parse JSON: {"key": value}' == str(exc_info.value)


def test_parse_json_non_string():
    # Test with a non-string value
    state = BaseState()
    expression = ConstantValueReference(123).parse_json()

    with pytest.raises(InvalidExpressionException) as exc_info:
        expression.resolve(state)

    # Verify the error message indicates type error
    assert "Expected a string, but got 123 of type <class 'int'>" == str(exc_info.value)
