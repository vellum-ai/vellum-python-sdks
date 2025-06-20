import inspect
from typing import Any, Dict

from pydantic import BaseModel

from vellum.workflows.utils.functions import _compile_annotation


def convert_pydantic_to_json_schema(schema_input: Any) -> Dict[str, Any]:
    """
    Convert a Pydantic model class, instance, or existing dict to a JSON schema.

    This function reuses the existing _compile_annotation logic but provides
    a simplified interface for single schema conversion without $defs references.

    Args:
        schema_input: Can be a Pydantic model class, instance, or existing dict

    Returns:
        JSON schema as a dictionary

    Raises:
        ValueError: If input is not a supported type
    """
    if isinstance(schema_input, dict):
        return schema_input

    if inspect.isclass(schema_input) and issubclass(schema_input, BaseModel):
        defs: Dict[str, Any] = {}
        result = _compile_annotation(schema_input, defs)

        if "$ref" in result and defs:
            ref_name = result["$ref"].split("/")[-1]
            if ref_name in defs:
                return defs[ref_name]

        return result
    elif isinstance(schema_input, BaseModel):
        return convert_pydantic_to_json_schema(schema_input.__class__)
    else:
        raise ValueError(f"Expected Pydantic model class/instance or dict, got {type(schema_input)}")
