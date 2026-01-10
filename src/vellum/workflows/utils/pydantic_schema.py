import inspect
from typing import Any, Dict, Type, TypeVar

import pydantic
from pydantic import BaseModel

from vellum.workflows.utils.functions import compile_annotation

T = TypeVar("T")
IS_PYDANTIC_V2 = pydantic.VERSION.startswith("2.")
_type_adapter_cache: Dict[Type, "pydantic.TypeAdapter"] = {}  # type: ignore[type-arg]


def validate_obj_as(type_: Type[T], object_: Any) -> T:
    """Validate an object as a given type using pydantic's TypeAdapter (v2) or parse_obj_as (v1).

    This is similar to parse_obj_as but without the convert_and_respect_annotation_metadata step,
    making it suitable for simple type validation without annotation metadata handling.
    """
    if IS_PYDANTIC_V2:
        if type_ not in _type_adapter_cache:
            _type_adapter_cache[type_] = pydantic.TypeAdapter(type_)  # type: ignore[attr-defined]
        return _type_adapter_cache[type_].validate_python(object_)
    return pydantic.parse_obj_as(type_, object_)  # type: ignore[attr-defined]


def normalize_json(schema_input: Any) -> Any:
    """
    Recursively normalize JSON data by converting Pydantic models to JSON schema.

    This function processes dictionaries recursively to find and convert any
    Pydantic model classes or instances to their JSON schema representation.

    Args:
        schema_input: Can be a Pydantic model class, instance, dict, or any other value

    Returns:
        Normalized JSON data with Pydantic models converted to JSON schema
    """
    if isinstance(schema_input, dict):
        return {key: normalize_json(value) for key, value in schema_input.items()}

    if inspect.isclass(schema_input) and issubclass(schema_input, BaseModel):
        defs: Dict[str, Any] = {}
        result = compile_annotation(schema_input, defs)

        if "$ref" in result and defs:
            ref_name = result["$ref"].split("/")[-1]
            if ref_name in defs:
                return defs[ref_name]

        return result
    elif isinstance(schema_input, BaseModel):
        return {key: normalize_json(getattr(schema_input, key)) for key in schema_input.__class__.model_fields.keys()}
    else:
        return schema_input
