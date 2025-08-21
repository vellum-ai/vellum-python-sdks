import pytest
from dataclasses import dataclass
from enum import Enum
from unittest.mock import Mock
from typing import Annotated, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field

from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.vellum_variable import VellumVariable
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.utils.functions import (
    compile_function_definition,
    compile_inline_workflow_function_definition,
    compile_workflow_deployment_function_definition,
)


def test_compile_function_definition__just_name():
    # GIVEN a function with just a name
    def my_function():
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={"type": "object", "properties": {}, "required": []},
    )


def test_compile_function_definition__docstring():
    # GIVEN a function with a docstring
    def my_function():
        """This is a test function"""
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        description="This is a test function",
        parameters={"type": "object", "properties": {}, "required": []},
    )


def test_compile_function_definition__all_args():
    # GIVEN a function with args of all base types
    def my_function(a: str, b: int, c: float, d: bool, e: list, f: dict):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "integer"},
                "c": {"type": "number"},
                "d": {"type": "boolean"},
                "e": {"type": "array"},
                "f": {"type": "object"},
            },
            "required": ["a", "b", "c", "d", "e", "f"],
        },
    )


def test_compile_function_definition__unions():
    # GIVEN a function with a union arg
    def my_function(a: Union[str, int]):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {
                "a": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
            },
            "required": ["a"],
        },
    )


def test_compile_function_definition__optionals():
    # GIVEN a function with various ways to specify optionals
    def my_function(
        a: str,
        b: Optional[str],
        c: None,
        d: str = "hello",
        e: Optional[str] = None,
    ):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "c": {"type": "null"},
                "d": {"type": "string", "default": "hello"},
                "e": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
            },
            "required": ["a", "b", "c"],
        },
    )


def test_compile_function_definition__parameterized_dicts():
    # GIVEN a function with a parameterized dict
    def my_function(a: Dict[str, int]):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "object", "additionalProperties": {"type": "integer"}},
            },
            "required": ["a"],
        },
    )


def test_compile_function_definition__parameterized_lists():
    # GIVEN a function with a parameterized list
    def my_function(a: List[int]):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "array", "items": {"type": "integer"}},
            },
            "required": ["a"],
        },
    )


def test_compile_function_definition__dataclasses():
    # GIVEN a function with a dataclass
    @dataclass
    class MyDataClass:
        a: int
        b: str

    def my_function(c: MyDataClass):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"c": {"$ref": "#/$defs/MyDataClass"}},
            "required": ["c"],
            "$defs": {
                "MyDataClass": {
                    "type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "string"}},
                    "required": ["a", "b"],
                }
            },
        },
    )


def test_compile_function_definition__pydantic():
    # GIVEN a function with a pydantic model
    class MyPydanticModel(BaseModel):
        a: int = Field(description="The first number")
        b: str

    def my_function(c: MyPydanticModel):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"c": {"$ref": "#/$defs/MyPydanticModel"}},
            "required": ["c"],
            "$defs": {
                "MyPydanticModel": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer", "description": "The first number"},
                        "b": {"type": "string"},
                    },
                    "required": ["a", "b"],
                }
            },
        },
    )


def test_compile_function_definition__default_dataclass():
    # GIVEN a function with a dataclass
    @dataclass
    class MyDataClass:
        a: int
        b: str

    def my_function(c: MyDataClass = MyDataClass(a=1, b="hello")):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"c": {"$ref": "#/$defs/MyDataClass", "default": {"a": 1, "b": "hello"}}},
            "required": [],
            "$defs": {
                "MyDataClass": {
                    "type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "string"}},
                    "required": ["a", "b"],
                }
            },
        },
    )


def test_compile_function_definition__default_pydantic():
    # GIVEN a function with a pydantic model as the default value
    class MyPydanticModel(BaseModel):
        a: int
        b: str

    def my_function(c: MyPydanticModel = MyPydanticModel(a=1, b="hello")):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"c": {"$ref": "#/$defs/MyPydanticModel", "default": {"a": 1, "b": "hello"}}},
            "required": [],
            "$defs": {
                "MyPydanticModel": {
                    "type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "string"}},
                    "required": ["a", "b"],
                }
            },
        },
    )


def test_compile_function_definition__lambda():
    # GIVEN a lambda
    lambda_function = lambda x: x + 1  # noqa: E731

    # WHEN compiling the function
    compiled_function = compile_function_definition(lambda_function)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="<lambda>",
        parameters={"type": "object", "properties": {"x": {"type": "null"}}, "required": ["x"]},
    )


def test_compile_inline_workflow_function_definition():
    class MyNode(BaseNode):
        pass

    class MyWorkflow(BaseWorkflow):
        graph = MyNode

    # WHEN compiling the function
    compiled_function = compile_inline_workflow_function_definition(MyWorkflow)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_workflow",
        parameters={"type": "object", "properties": {}, "required": []},
    )


def test_compile_inline_workflow_function_definition__docstring():
    class MyNode(BaseNode):
        pass

    class MyWorkflow(BaseWorkflow):
        """
        This is a test workflow
        """

        graph = MyNode

    # WHEN compiling the function
    compiled_function = compile_inline_workflow_function_definition(MyWorkflow)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_workflow",
        description="\n        This is a test workflow\n        ",
        parameters={"type": "object", "properties": {}, "required": []},
    )


def test_compile_inline_workflow_function_definition__all_args():
    class MyInputs(BaseInputs):
        a: str
        b: int
        c: float
        d: bool
        e: list
        f: dict

    class MyNode(BaseNode):
        pass

    class MyWorkflow(BaseWorkflow[MyInputs, BaseState]):
        graph = MyNode

    # WHEN compiling the workflow
    compiled_function = compile_inline_workflow_function_definition(MyWorkflow)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_workflow",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "integer"},
                "c": {"type": "number"},
                "d": {"type": "boolean"},
                "e": {"type": "array"},
                "f": {"type": "object"},
            },
            "required": ["a", "b", "c", "d", "e", "f"],
        },
    )


def test_compile_inline_workflow_function_definition__unions():
    # GIVEN a workflow with a union
    class MyInputs(BaseInputs):
        a: Union[str, int]

    class MyNode(BaseNode):
        pass

    class MyWorkflow(BaseWorkflow[MyInputs, BaseState]):
        graph = MyNode

    # WHEN compiling the workflow
    compiled_function = compile_inline_workflow_function_definition(MyWorkflow)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_workflow",
        parameters={
            "type": "object",
            "properties": {"a": {"anyOf": [{"type": "string"}, {"type": "integer"}]}},
            "required": ["a"],
        },
    )


def test_compile_inline_workflow_function_definition__optionals():
    class MyInputs(BaseInputs):
        a: str
        b: Optional[str]
        c: None
        d: str = "hello"
        e: Optional[str] = None

    class MyNode(BaseNode):
        pass

    class MyWorkflow(BaseWorkflow[MyInputs, BaseState]):
        graph = MyNode

    # WHEN compiling the workflow
    compiled_function = compile_inline_workflow_function_definition(MyWorkflow)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_workflow",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "c": {"type": "null"},
                "d": {"type": "string", "default": "hello"},
                "e": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
            },
            "required": ["a", "b", "c"],
        },
    )


def test_compile_workflow_deployment_function_definition__just_name():
    # GIVEN a mock Vellum client and deployment
    mock_client = Mock()
    mock_release = Mock()
    mock_release.workflow_version.input_variables = []
    mock_release.description = "This is a test deployment"
    mock_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = mock_release

    deployment_config = {"deployment": "my_deployment", "release_tag": "latest"}

    # WHEN compiling the deployment workflow function
    compiled_function = compile_workflow_deployment_function_definition(deployment_config, mock_client)

    # THEN it should return the compiled function definition (same structure as function test)
    assert compiled_function == FunctionDefinition(
        name="my_deployment",
        description="This is a test deployment",
        parameters={"type": "object", "properties": {}, "required": []},
    )


def test_compile_workflow_deployment_function_definition__all_args():
    # GIVEN a mock Vellum client and deployment
    mock_client = Mock()
    mock_release = Mock()

    mock_inputs = []
    for key, vellum_type in [
        ("a", "STRING"),
        ("b", "NUMBER"),
        ("c", "JSON"),
        ("d", "CHAT_HISTORY"),
        ("e", "SEARCH_RESULTS"),
        ("f", "ERROR"),
        ("g", "ARRAY"),
        ("h", "FUNCTION_CALL"),
        ("i", "IMAGE"),
        ("j", "AUDIO"),
        ("k", "DOCUMENT"),
        ("l", "NULL"),
    ]:
        mock_input = VellumVariable(
            id=f"input_{key}",
            key=key,
            type=vellum_type,
            required=True,
            default=None,
        )
        mock_inputs.append(mock_input)

    mock_release.workflow_version.input_variables = mock_inputs
    mock_release.description = "This is a test deployment"
    mock_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = mock_release

    deployment_config = {"deployment": "my_deployment", "release_tag": "latest"}

    # WHEN compiling the deployment workflow function
    compiled_function = compile_workflow_deployment_function_definition(deployment_config, mock_client)

    # THEN it should return the compiled function definition
    assert compiled_function == FunctionDefinition(
        name="my_deployment",
        description="This is a test deployment",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "number"},
                "c": {"type": "object"},
                "d": {"type": "array"},
                "e": {"type": "array"},
                "f": {"type": "object"},
                "g": {"type": "array"},
                "h": {"type": "object"},
                "i": {"type": "object"},
                "j": {"type": "object"},
                "k": {"type": "object"},
                "l": {"type": "null"},
            },
            "required": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"],
        },
    )


def test_compile_workflow_deployment_function_definition__defaults():
    # GIVEN a mock Vellum client and deployment
    mock_client = Mock()
    mock_release = Mock()

    mock_inputs = []

    mock_input_no_default = VellumVariable(
        id="no_default",
        key="no_default",
        type="STRING",
        required=True,
        default=None,
    )
    mock_inputs.append(mock_input_no_default)

    mock_input_null_default = VellumVariable(
        id="null_default",
        key="null_default",
        type="STRING",
        required=False,
        default=StringVellumValue(value=None),
    )
    mock_inputs.append(mock_input_null_default)

    mock_input_actual_default = VellumVariable(
        id="actual_default",
        key="actual_default",
        type="STRING",
        required=False,
        default=StringVellumValue(value="hello world"),
    )
    mock_inputs.append(mock_input_actual_default)

    mock_release.workflow_version.input_variables = mock_inputs
    mock_release.description = "This is a test deployment"
    mock_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = mock_release

    deployment_config = {"deployment": "my_deployment", "release_tag": "latest"}

    # WHEN compiling the deployment workflow function
    compiled_function = compile_workflow_deployment_function_definition(deployment_config, mock_client)

    # THEN it should return the compiled function definition with proper default handling
    assert compiled_function == FunctionDefinition(
        name="my_deployment",
        description="This is a test deployment",
        parameters={
            "type": "object",
            "properties": {
                "no_default": {"type": "string"},
                "null_default": {"type": "string", "default": None},
                "actual_default": {"type": "string", "default": "hello world"},
            },
            "required": ["no_default"],
        },
    )


@pytest.mark.parametrize(
    "annotation,expected_schema",
    [
        (Literal["a", "b"], {"type": "string", "enum": ["a", "b"]}),
        (Literal["a", 1], {"enum": ["a", 1]}),
    ],
)
def test_compile_function_definition__literal(annotation, expected_schema):
    def my_function(a: annotation):  # type: ignore
        pass

    compiled_function = compile_function_definition(my_function)
    assert isinstance(compiled_function.parameters, dict)
    assert compiled_function.parameters["properties"]["a"] == expected_schema


def test_compile_function_definition__literal_type_not_in_map():
    class MyEnum(Enum):
        FOO = "foo"
        BAR = "bar"

    def my_function(a: Literal[MyEnum.FOO, MyEnum.BAR]):
        pass

    compiled_function = compile_function_definition(my_function)
    assert isinstance(compiled_function.parameters, dict)
    assert compiled_function.parameters["properties"]["a"] == {"enum": [MyEnum.FOO, MyEnum.BAR]}


def test_compile_function_definition__annotated_descriptions():
    # GIVEN a function with annotated parameters that include descriptions
    def my_function(
        bar: Annotated[str, "My bar parameter"],
        other: Annotated[int, "My other parameter"],
        regular_param: str,
        optional_param: Annotated[bool, "Optional boolean parameter"] = True,
    ):
        """Test function with annotated parameters."""
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition with descriptions
    assert compiled_function == FunctionDefinition(
        name="my_function",
        description="Test function with annotated parameters.",
        parameters={
            "type": "object",
            "properties": {
                "bar": {"type": "string", "description": "My bar parameter"},
                "other": {"type": "integer", "description": "My other parameter"},
                "regular_param": {"type": "string"},
                "optional_param": {"type": "boolean", "description": "Optional boolean parameter", "default": True},
            },
            "required": ["bar", "other", "regular_param"],
        },
    )


def test_compile_function_definition__annotated_without_description():
    # GIVEN a function with annotated parameters but no description metadata
    def my_function(param: Annotated[str, None]):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition without description
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {
                "param": {"type": "string"},
            },
            "required": ["param"],
        },
    )


def test_compile_function_definition__annotated_complex_types():
    # GIVEN a function with annotated types
    def my_function(
        location: Annotated[Literal["New York", "Portland"], "The location you found"],
        items: Annotated[List[str], "List of string items"],
        config: Annotated[Dict[str, int], "Configuration mapping"],
    ):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition with descriptions for complex types
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "enum": ["New York", "Portland"],
                    "description": "The location you found",
                },
                "items": {"type": "array", "items": {"type": "string"}, "description": "List of string items"},
                "config": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                    "description": "Configuration mapping",
                },
            },
            "required": ["location", "items", "config"],
        },
    )


@pytest.mark.parametrize(
    "annotation,expected_schema",
    [
        (
            Tuple[int, ...],
            {"type": "array", "items": {"type": "integer"}},
        ),
        (
            Tuple[int, str],
            {
                "type": "array",
                "prefixItems": [{"type": "integer"}, {"type": "string"}],
                "minItems": 2,
                "maxItems": 2,
            },
        ),
    ],
)
def test_compile_function_definition__tuples(annotation, expected_schema):
    def my_function(a: annotation):  # type: ignore
        pass

    compiled_function = compile_function_definition(my_function)
    assert isinstance(compiled_function.parameters, dict)
    assert compiled_function.parameters["properties"]["a"] == expected_schema
