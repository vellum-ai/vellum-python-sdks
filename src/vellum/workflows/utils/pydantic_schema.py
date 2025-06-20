import inspect
from typing import Any, Dict

from pydantic import BaseModel

from vellum.workflows.utils.functions import compile_annotation


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
