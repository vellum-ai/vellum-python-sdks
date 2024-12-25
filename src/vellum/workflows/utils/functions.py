import dataclasses
import inspect
from typing import Any, Callable, Optional, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from vellum.client.types.function_definition import FunctionDefinition

type_map = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
    None: "null",
    type(None): "null",
}


def _compile_annotation(annotation: Optional[Any], defs: dict[str, Any]) -> dict:
    if annotation is None:
        return {"type": "null"}

    if get_origin(annotation) is Union:
        return {"anyOf": [_compile_annotation(a, defs) for a in get_args(annotation)]}

    if get_origin(annotation) is dict:
        _, value_type = get_args(annotation)
        return {"type": "object", "additionalProperties": _compile_annotation(value_type, defs)}

    if get_origin(annotation) is list:
        item_type = get_args(annotation)[0]
        return {"type": "array", "items": _compile_annotation(item_type, defs)}

    if dataclasses.is_dataclass(annotation):
        if annotation.__name__ not in defs:
            properties = {}
            required = []
            for field in dataclasses.fields(annotation):
                properties[field.name] = _compile_annotation(field.type, defs)
                if field.default is dataclasses.MISSING:
                    required.append(field.name)
                else:
                    properties[field.name]["default"] = _compile_default_value(field.default)
            defs[annotation.__name__] = {"type": "object", "properties": properties, "required": required}
        return {"$ref": f"#/$defs/{annotation.__name__}"}

    if issubclass(annotation, BaseModel):
        if annotation.__name__ not in defs:
            properties = {}
            required = []
            for field_name, field in annotation.model_fields.items():
                # Mypy is incorrect here, the `annotation` attribute is defined on `FieldInfo`
                field_annotation = field.annotation  # type: ignore[attr-defined]
                properties[field_name] = _compile_annotation(field_annotation, defs)
                if field.default is PydanticUndefined:
                    required.append(field_name)
                else:
                    properties[field_name]["default"] = _compile_default_value(field.default)
            defs[annotation.__name__] = {"type": "object", "properties": properties, "required": required}

        return {"$ref": f"#/$defs/{annotation.__name__}"}

    return {"type": type_map[annotation]}


def _compile_default_value(default: Any) -> Any:
    if dataclasses.is_dataclass(default):
        return {
            field.name: _compile_default_value(getattr(default, field.name)) for field in dataclasses.fields(default)
        }

    if isinstance(default, BaseModel):
        return {
            field_name: _compile_default_value(getattr(default, field_name))
            for field_name in default.model_fields.keys()
        }

    return default


def compile_function_definition(function: Callable) -> FunctionDefinition:
    """
    Converts a Python function into our Vellum-native FunctionDefinition type.
    """

    try:
        signature = inspect.signature(function)
    except ValueError as e:
        raise ValueError(f"Failed to get signature for function {function.__name__}: {str(e)}")

    properties = {}
    required = []
    defs: dict[str, Any] = {}
    for param in signature.parameters.values():
        properties[param.name] = _compile_annotation(param.annotation, defs)
        if param.default is inspect.Parameter.empty:
            required.append(param.name)
        else:
            properties[param.name]["default"] = _compile_default_value(param.default)

    parameters = {"type": "object", "properties": properties, "required": required}
    if defs:
        parameters["$defs"] = defs

    return FunctionDefinition(
        name=function.__name__,
        parameters=parameters,
    )
