import pytest
from dataclasses import dataclass
from enum import Enum
import sys
import types
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
from vellum.workflows.types.definition import DeploymentDefinition
from vellum.workflows.utils.functions import (
    compile_annotation,
    compile_function_definition,
    compile_inline_workflow_function_definition,
    compile_workflow_deployment_function_definition,
    tool,
    use_tool_inputs,
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
    ref_name = f"{__name__}.test_compile_function_definition__dataclasses.<locals>.MyDataClass"
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"c": {"$ref": f"#/$defs/{ref_name}"}},
            "required": ["c"],
            "$defs": {
                ref_name: {
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
    ref_name = f"{__name__}.test_compile_function_definition__pydantic.<locals>.MyPydanticModel"
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"c": {"$ref": f"#/$defs/{ref_name}"}},
            "required": ["c"],
            "$defs": {
                ref_name: {
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
    ref_name = f"{__name__}.test_compile_function_definition__default_dataclass.<locals>.MyDataClass"
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"c": {"$ref": f"#/$defs/{ref_name}", "default": {"a": 1, "b": "hello"}}},
            "required": [],
            "$defs": {
                ref_name: {
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
    ref_name = f"{__name__}.test_compile_function_definition__default_pydantic.<locals>.MyPydanticModel"
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"c": {"$ref": f"#/$defs/{ref_name}", "default": {"a": 1, "b": "hello"}}},
            "required": [],
            "$defs": {
                ref_name: {
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
    mock_release.deployment.name = "my_deployment"
    mock_release.workflow_version.input_variables = []
    mock_release.description = "This is a test deployment"
    mock_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = mock_release

    deployment_definition = DeploymentDefinition(deployment="my_deployment", release_tag="LATEST")

    # WHEN compiling the deployment workflow function
    compiled_function = compile_workflow_deployment_function_definition(deployment_definition, mock_client)

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
    mock_release.deployment.name = "my_deployment"
    mock_release.description = "This is a test deployment"
    mock_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = mock_release

    deployment_definition = DeploymentDefinition(deployment="my_deployment", release_tag="latest")

    # WHEN compiling the deployment workflow function
    compiled_function = compile_workflow_deployment_function_definition(deployment_definition, mock_client)

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
    mock_release.deployment.name = "my_deployment"
    mock_release.description = "This is a test deployment"
    mock_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = mock_release

    deployment_definition = DeploymentDefinition(deployment="my_deployment", release_tag="LATEST")

    # WHEN compiling the deployment workflow function
    compiled_function = compile_workflow_deployment_function_definition(deployment_definition, mock_client)

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


def test_compile_function_definition__string_annotations_with_future_imports():
    """Test that string annotations work with __future__ import annotations."""
    # This simulates what happens when using `from __future__ import annotations`
    # where type annotations become string literals at runtime

    def my_function_with_string_annotations(
        a: "str",
        b: "int",
        c: "float",
        d: "bool",
        e: "list",
        f: "dict",
        g: "None",
    ):
        """Function with string type annotations."""
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function_with_string_annotations)

    # THEN it should return the compiled function definition with proper types
    assert compiled_function == FunctionDefinition(
        name="my_function_with_string_annotations",
        description="Function with string type annotations.",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "integer"},
                "c": {"type": "number"},
                "d": {"type": "boolean"},
                "e": {"type": "array"},
                "f": {"type": "object"},
                "g": {"type": "null"},
            },
            "required": ["a", "b", "c", "d", "e", "f", "g"],
        },
    )


def test_use_tool_inputs__inline_vs_decorator():
    """
    Tests that inline use_tool_inputs(...)(func) behaves the same as @use_tool_inputs(...) decorator.
    """

    # GIVEN a function with some parameters
    def my_function(a: str, b: int, c: float) -> str:
        """A test function."""
        return f"{a}-{b}-{c}"

    # WHEN using use_tool_inputs as a decorator
    @use_tool_inputs(a="fixed_a", b=42)
    def decorated_function(a: str, b: int, c: float) -> str:
        """A test function."""
        return f"{a}-{b}-{c}"

    # AND using use_tool_inputs inline
    inline_function = use_tool_inputs(a="fixed_a", b=42)(my_function)

    # THEN both should have the same __vellum_inputs__ attribute
    assert hasattr(decorated_function, "__vellum_inputs__")
    assert hasattr(inline_function, "__vellum_inputs__")

    # AND the inputs should be identical
    assert decorated_function.__vellum_inputs__ == inline_function.__vellum_inputs__
    assert decorated_function.__vellum_inputs__ == {"a": "fixed_a", "b": 42}


def test_tool__inline_vs_decorator():
    """
    Tests that inline tool(inputs={...})(func) behaves the same as @tool(inputs={...}) decorator.
    """

    # GIVEN a function with some parameters
    def my_function(a: str, b: int, c: float) -> str:
        """A test function."""
        return f"{a}-{b}-{c}"

    # WHEN using tool as a decorator
    @tool(inputs={"a": "fixed_a", "b": 42})
    def decorated_function(a: str, b: int, c: float) -> str:
        """A test function."""
        return f"{a}-{b}-{c}"

    # AND using tool inline
    inline_function = tool(inputs={"a": "fixed_a", "b": 42})(my_function)

    # THEN both should have the same __vellum_inputs__ attribute
    assert hasattr(decorated_function, "__vellum_inputs__")
    assert hasattr(inline_function, "__vellum_inputs__")

    # AND the inputs should be identical
    assert decorated_function.__vellum_inputs__ == inline_function.__vellum_inputs__
    assert decorated_function.__vellum_inputs__ == {"a": "fixed_a", "b": 42}


def test_tool__backward_compatibility_with_use_tool_inputs():
    """
    Tests that tool(inputs={...}) and use_tool_inputs(**inputs) produce the same __vellum_inputs__ attribute.
    """

    # GIVEN a function with some parameters
    def my_function(a: str, b: int) -> str:
        """A test function."""
        return f"{a}-{b}"

    # WHEN using tool as a decorator with inputs dict
    @tool(inputs={"a": "value_a"})
    def tool_decorated(a: str, b: int) -> str:
        """A test function."""
        return f"{a}-{b}"

    # AND using use_tool_inputs as a decorator with kwargs
    @use_tool_inputs(a="value_a")
    def use_tool_inputs_decorated(a: str, b: int) -> str:
        """A test function."""
        return f"{a}-{b}"

    # THEN both should have identical __vellum_inputs__ attributes
    assert getattr(tool_decorated, "__vellum_inputs__") == getattr(use_tool_inputs_decorated, "__vellum_inputs__")
    assert getattr(tool_decorated, "__vellum_inputs__") == {"a": "value_a"}


def test_tool_examples_included_in_schema():
    @tool(
        examples=[
            {"location": "San Francisco"},
            {"location": "New York", "units": "celsius"},
        ]
    )
    def get_current_weather(location: str, units: str = "fahrenheit") -> str:
        return "sunny"

    compiled = compile_function_definition(get_current_weather)
    assert isinstance(compiled.parameters, dict)
    assert compiled.parameters == {
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "units": {"type": "string", "default": "fahrenheit"},
        },
        "required": ["location"],
        "examples": [
            {"location": "San Francisco"},
            {"location": "New York", "units": "celsius"},
        ],
    }


def test_compile_function_definition__simple_class():
    """
    Tests that a function with a simple class parameter compiles correctly.
    """

    # GIVEN a simple class with __init__ method
    class SimpleClass:
        def __init__(self, name: str, count: int):
            self.name = name
            self.count = count

    # AND a function that takes the simple class as a parameter
    def my_function(data: SimpleClass):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition with the class properties
    ref_name = f"{__name__}.test_compile_function_definition__simple_class.<locals>.SimpleClass"
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"data": {"$ref": f"#/$defs/{ref_name}"}},
            "required": ["data"],
            "$defs": {
                ref_name: {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "count": {"type": "integer"}},
                    "required": ["name", "count"],
                }
            },
        },
    )


def test_compile_function_definition__simple_class_with_defaults():
    """
    Tests that a function with a simple class parameter with default values compiles correctly.
    """

    # GIVEN a simple class with __init__ method that has default values
    class SimpleClassWithDefaults:
        def __init__(self, name: str, count: int = 10):
            self.name = name
            self.count = count

    # AND a function that takes the simple class as a parameter
    def my_function(data: SimpleClassWithDefaults):
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN it should return the compiled function definition with the class properties
    ref_name = (
        f"{__name__}.test_compile_function_definition__simple_class_with_defaults.<locals>.SimpleClassWithDefaults"
    )
    assert compiled_function == FunctionDefinition(
        name="my_function",
        parameters={
            "type": "object",
            "properties": {"data": {"$ref": f"#/$defs/{ref_name}"}},
            "required": ["data"],
            "$defs": {
                ref_name: {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "count": {"type": "integer", "default": 10},
                    },
                    "required": ["name"],
                }
            },
        },
    )


class StringEnum(Enum):
    FOO = "foo"
    BAR = "bar"


class IntEnum(Enum):
    ONE = 1
    TWO = 2


class MixedEnum(Enum):
    FOO = "foo"
    ONE = 1


@pytest.mark.parametrize(
    "enum_class,expected_schema",
    [
        (StringEnum, {"type": "string", "enum": ["foo", "bar"]}),
        (IntEnum, {"type": "integer", "enum": [1, 2]}),
        (MixedEnum, {"enum": ["foo", 1]}),
    ],
)
def test_compile_function_definition__enum_type(enum_class, expected_schema):
    """Tests that Enum class types are compiled to JSON schema with enum values."""

    # GIVEN a function with an Enum type parameter
    def my_function(a: enum_class):  # type: ignore[valid-type]
        pass

    # WHEN compiling the function
    compiled_function = compile_function_definition(my_function)

    # THEN the parameter should have the expected enum schema
    assert isinstance(compiled_function.parameters, dict)
    assert compiled_function.parameters["properties"]["a"] == expected_schema


@pytest.mark.skipif(sys.version_info < (3, 10), reason="PEP 604 union types are only available on Python 3.10+")
def test_compile_annotation__pep604_union():
    """Tests that PEP 604 union types (str | None) are compiled correctly on Python 3.10+."""

    # GIVEN a PEP 604 union type (only available as runtime object on Python 3.10+)
    pep604_union = eval("str | None")
    assert isinstance(pep604_union, types.UnionType)  # type: ignore[attr-defined]

    # WHEN compiling the annotation
    result = compile_annotation(pep604_union, {})

    # THEN it should return the correct schema with anyOf
    assert result == {"anyOf": [{"type": "string"}, {"type": "null"}]}


@pytest.mark.skipif(sys.version_info < (3, 10), reason="PEP 604 union types are only available on Python 3.10+")
def test_compile_annotation__pep604_union_multiple_types():
    """Tests that PEP 604 union types with multiple types are compiled correctly."""

    # GIVEN a PEP 604 union type with multiple types
    pep604_union = eval("str | int | None")
    assert isinstance(pep604_union, types.UnionType)  # type: ignore[attr-defined]

    # WHEN compiling the annotation
    result = compile_annotation(pep604_union, {})

    # THEN it should return the correct schema with anyOf
    assert result == {"anyOf": [{"type": "string"}, {"type": "integer"}, {"type": "null"}]}
