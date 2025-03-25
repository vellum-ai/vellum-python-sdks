import pytest
from typing import Any, List, Union

from pydantic import BaseModel

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.function_call import FunctionCall as FunctionCallType
from vellum.client.types.vellum_value import VellumValue
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.utils import cast_to_output_type, parse_type_from_str
from vellum.workflows.types.core import Json


class Person(BaseModel):
    name: str
    age: int


class FunctionCall(BaseModel):
    name: str
    args: List[int]


@pytest.mark.parametrize(
    "input_str, output_type, expected_result",
    [
        ("hello", str, "hello"),
        ("3.14", float, 3.14),
        ("42", int, 42),
        ("True", bool, True),
        ("", List[str], []),  # Empty string should return an empty list
        ("[1, 2, 3]", List[int], [1, 2, 3]),
        ('["a", "b", "c"]', List[str], ["a", "b", "c"]),
        ('{"name": "Alice", "age": 30}', Json, {"name": "Alice", "age": 30}),
        (
            '{"type": "FUNCTION_CALL", "value": {"name": "test", "args": [1, 2]}}',
            Json,
            {"name": "test", "args": [1, 2]},
        ),
        ("42", Union[int, str], 42),
        ("hello", Union[int, str], "hello"),
    ],
    ids=[
        "str",
        "float",
        "int",
        "bool",
        "empty_list",
        "list_of_int",
        "list_of_str",
        "simple_json",
        "function_call_json",
        "union_int",
        "union_str",
    ],
)
def test_parse_type_from_str_basic_cases(input_str, output_type, expected_result):
    result = parse_type_from_str(input_str, output_type)
    assert result == expected_result


def test_parse_type_from_str_pydantic_models():
    person_json = '{"name": "Alice", "age": 30}'
    person = parse_type_from_str(person_json, Person)
    assert isinstance(person, Person)
    assert person.name == "Alice"
    assert person.age == 30

    function_json = '{"name": "test", "args": [1, 2]}'
    function = parse_type_from_str(function_json, FunctionCall)
    assert isinstance(function, FunctionCall)
    assert function.name == "test"
    assert function.args == [1, 2]

    function_call_json = '{"value": {"name": "test", "args": [1, 2]}}'
    function = parse_type_from_str(function_call_json, FunctionCall)
    assert isinstance(function, FunctionCall)
    assert function.name == "test"
    assert function.args == [1, 2]


def test_parse_type_from_str_list_of_models():
    person_list_json = '[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'
    persons = parse_type_from_str(person_list_json, List[Person])
    assert len(persons) == 2
    assert all(isinstance(p, Person) for p in persons)
    assert persons[0].name == "Alice"
    assert persons[0].age == 30
    assert persons[1].name == "Bob"
    assert persons[1].age == 25


@pytest.mark.parametrize(
    "input_str, output_type, expected_exception, expected_code, expected_message",
    [
        (
            "{invalid json}",
            List[str],
            NodeException,
            WorkflowErrorCode.INVALID_OUTPUTS,
            "Invalid JSON Array format for result_as_str",
        ),
        (
            "{invalid json}",
            Person,
            NodeException,
            WorkflowErrorCode.INVALID_OUTPUTS,
            "Invalid JSON format for result_as_str",
        ),
        (
            "{invalid json}",
            Json,
            NodeException,
            WorkflowErrorCode.INVALID_OUTPUTS,
            "Invalid JSON format for result_as_str",
        ),
        ('{"name": "Alice"}', List[str], ValueError, None, "Expected a list of items for result_as_str, received dict"),
        ("data", object, ValueError, None, "Unsupported output type: <class 'object'>"),
    ],
    ids=[
        "invalid_json_list",
        "invalid_json_model",
        "invalid_json_json_type",
        "non_list_for_list",
        "unsupported_type",
    ],
)
def test_parse_type_from_str_error_cases(input_str, output_type, expected_exception, expected_code, expected_message):
    with pytest.raises(expected_exception) as excinfo:
        parse_type_from_str(input_str, output_type)

    if expected_code:
        assert excinfo.value.code == expected_code

    assert expected_message in str(excinfo.value)


@pytest.mark.parametrize(
    "output_type,expected_result",
    [
        (str, ""),  # String
        (int, 0),  # Number
        (float, 0.0),  # Number
        (Any, None),  # Json
        (FunctionCallType, {}),  # FunctionCall
        (List[ChatMessage], []),  # Chat History
        (List[VellumValue], []),  # Array
        (Union[float, int], 0.0),  # Union
    ],
    ids=[
        "string",
        "integer",
        "float",
        "json",
        "function_call",
        "chat_history",
        "array",
        "union",
    ],
)
def test_cast_to_output_type_none_value(output_type, expected_result):
    """Test that cast_to_output_type returns appropriate default values when None is provided."""
    result = cast_to_output_type(None, output_type)
    assert result == expected_result
