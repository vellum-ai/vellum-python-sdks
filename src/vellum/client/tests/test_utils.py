import uuid
from unittest.mock import Mock
from vellum.client.utils import convert_input_variable_to_uuid


def test_convert_input_variable_to_uuid_with_valid_uuid():
    """Test convert_input_variable_to_uuid with valid UUID passes through unchanged."""
    uuid_value = "123e4567-e89b-12d3-a456-426614174000"

    # GIVEN a valid UUID
    # WHEN the function is called
    result = convert_input_variable_to_uuid(uuid_value)

    # THEN the result should be the original UUID unchanged
    assert result == uuid_value


def test_convert_input_variable_to_uuid_with_invalid_uuid_converts():
    """Test convert_input_variable_to_uuid with invalid UUID gets converted to UUID."""
    non_uuid_value = "some_variable_name"
    executable_id = "test_executable_123"

    # GIVEN an invalid UUID with context
    mock_info = Mock()
    mock_info.context = {"executable_id": executable_id}

    # WHEN the function is called
    result = convert_input_variable_to_uuid(non_uuid_value, mock_info)

    # THEN it should return a different value
    assert result != non_uuid_value

    # AND it's a valid UUID
    uuid.UUID(result)  # This will raise ValueError if not a valid UUID
