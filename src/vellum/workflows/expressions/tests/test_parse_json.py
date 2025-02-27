import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


def test_parse_json_invalid_json():
    # GIVEN an invalid JSON string
    state = BaseState()
    expression = ConstantValueReference('{"key": value}').parse_json()

    # WHEN we attempt to resolve the expression
    with pytest.raises(InvalidExpressionException) as exc_info:
        expression.resolve(state)

    # THEN an exception should be raised
    assert "Failed to parse JSON" in str(exc_info.value)


def test_parse_json_invalid_type():
    # GIVEN a non-string value
    state = BaseState()
    expression = ConstantValueReference(123).parse_json()

    # WHEN we attempt to resolve the expression
    with pytest.raises(InvalidExpressionException) as exc_info:
        expression.resolve(state)

    # THEN an exception should be raised
    assert "Expected a string, but got 123 of type <class 'int'>" == str(exc_info.value)
