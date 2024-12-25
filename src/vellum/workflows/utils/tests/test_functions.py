from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from vellum.client.types.function_definition import FunctionDefinition
from vellum.workflows.utils.functions import compile_function_definition


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
        a: int
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
                    "properties": {"a": {"type": "integer"}, "b": {"type": "string"}},
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
