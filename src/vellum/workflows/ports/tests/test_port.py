import pytest
from unittest.mock import Mock

from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import ConditionType


@pytest.mark.parametrize(
    "condition_value,expected",
    [
        # Truthy values
        (True, True),
        (1, True),
        ("hello", True),
        ([1, 2, 3], True),
        ({"key": "value"}, True),
        (1.5, True),
        (-1, True),
        # Falsy values
        (False, False),
        (0, False),
        ("", False),
        ([], False),
        ({}, False),
        (0.0, False),
        (None, False),
    ],
)
def test_port_on_if_with_non_descriptor_values(condition_value, expected):
    """Test that Port.on_if() correctly handles non-descriptor values."""

    # Given a port with a non-descriptor value
    port = Port.on_if(condition_value)

    # Then the port properties should be correct
    assert port._condition_type == ConditionType.IF
    assert port._condition == condition_value

    # When we resolve the condition
    mock_state = Mock(spec=BaseState)
    result = port.resolve_condition(mock_state)

    # Then the result should be correct
    assert result == expected
