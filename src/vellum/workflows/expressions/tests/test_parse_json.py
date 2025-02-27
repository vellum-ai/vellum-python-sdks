import pytest

from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state.base import BaseState


def test_parse_json():
    # GIVEN a valid JSON string
    state = BaseState()
    expression = ConstantValueReference('{"key": "value"}').parse_json()

    # WHEN we attempt to resolve the expression
    result = expression.resolve(state)

    # THEN the JSON should be parsed successfully
    assert result == {"key": "value"}


def test_parse_json_array():
    # GIVEN a valid JSON array
    state = BaseState()
    expression = ConstantValueReference("[1, 2, 3]").parse_json()

    # WHEN we attempt to resolve the expression
    result = expression.resolve(state)

    # THEN the JSON should be parsed successfully
    assert result == [1, 2, 3]


def test_parse_json_bytes():
    # GIVEN a valid JSON as bytes
    state = BaseState()
    json_bytes = b'{"key": "value"}'
    expression = ConstantValueReference(json_bytes).parse_json()

    # WHEN we attempt to resolve the expression
    result = expression.resolve(state)

    # THEN the JSON should be parsed successfully
    assert result == {"key": "value"}


def test_parse_json_bytearray():
    # GIVEN a valid JSON as bytearray
    state = BaseState()
    json_bytearray = bytearray(b'{"key": "value"}')
    expression = ConstantValueReference(json_bytearray).parse_json()

    # WHEN we attempt to resolve the expression
    result = expression.resolve(state)

    # THEN the JSON should be parsed successfully
    assert result == {"key": "value"}


def test_parse_json_bytes_with_utf8_chars():
    # GIVEN a valid JSON as bytes with UTF-8 characters
    state = BaseState()
    json_bytes = b'{"key": "\xf0\x9f\x8c\x9f"}'  # UTF-8 encoded star emoji
    expression = ConstantValueReference(json_bytes).parse_json()

    # WHEN we attempt to resolve the expression
    result = expression.resolve(state)

    # THEN the JSON should be parsed successfully
    assert result == {"key": "🌟"}


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
