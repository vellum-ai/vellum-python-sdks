import dataclasses
import inspect
from typing import TYPE_CHECKING, Any, Callable, Dict, Literal, Optional, Type, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from pydash import snake_case

from vellum import Vellum
from vellum.client.types.function_definition import FunctionDefinition
from vellum.workflows.utils.vellum_variables import vellum_variable_type_to_openapi_type

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow

type_map = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
    None: "null",
    type(None): "null",
    inspect._empty: "null",
}


def compile_annotation(annotation: Optional[Any], defs: dict[str, Any]) -> dict:
    if annotation is None:
        return {"type": "null"}

    if get_origin(annotation) is Union:
        return {"anyOf": [compile_annotation(a, defs) for a in get_args(annotation)]}

    if get_origin(annotation) is Literal:
        values = list(get_args(annotation))
        types = {type(value) for value in values}
        if len(types) == 1:
            value_type = types.pop()
            if value_type in type_map:
                return {"type": type_map[value_type], "enum": values}
            else:
                return {"enum": values}
        else:
            return {"enum": values}

    if get_origin(annotation) is dict:
        _, value_type = get_args(annotation)
        return {"type": "object", "additionalProperties": compile_annotation(value_type, defs)}

    if get_origin(annotation) is list:
        item_type = get_args(annotation)[0]
        return {"type": "array", "items": compile_annotation(item_type, defs)}

    if dataclasses.is_dataclass(annotation):
        if annotation.__name__ not in defs:
            properties = {}
            required = []
            for field in dataclasses.fields(annotation):
                properties[field.name] = compile_annotation(field.type, defs)
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
                properties[field_name] = compile_annotation(field_annotation, defs)
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
            for field_name in default.__class__.model_fields.keys()
        }

    return default


def _compile_workflow_deployment_input(input_var: Any) -> dict[str, Any]:
    """
    Converts a deployment workflow input variable to a JSON schema type definition.
    """
    primitive_type = vellum_variable_type_to_openapi_type(input_var.type)
    input_schema = {"type": primitive_type}

    if input_var.default is not None:
        input_schema["default"] = input_var.default.value

    return input_schema


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
        properties[param.name] = compile_annotation(param.annotation, defs)
        if param.default is inspect.Parameter.empty:
            required.append(param.name)
        else:
            properties[param.name]["default"] = _compile_default_value(param.default)

    parameters = {"type": "object", "properties": properties, "required": required}
    if defs:
        parameters["$defs"] = defs

    return FunctionDefinition(
        name=function.__name__,
        description=function.__doc__,
        parameters=parameters,
    )


def compile_inline_workflow_function_definition(workflow_class: Type["BaseWorkflow"]) -> FunctionDefinition:
    """
    Converts a base workflow class into our Vellum-native FunctionDefinition type.
    """
    # Get the inputs class for the workflow
    inputs_class = workflow_class.get_inputs_class()
    vars_inputs_class = vars(inputs_class)

    properties = {}
    required = []
    defs: dict[str, Any] = {}

    for name, field_type in inputs_class.__annotations__.items():
        if name.startswith("__"):
            continue

        properties[name] = compile_annotation(field_type, defs)

        # Check if the field has a default value
        if name not in vars_inputs_class:
            required.append(name)
        else:
            # Field has a default value
            properties[name]["default"] = vars_inputs_class[name]

    parameters = {"type": "object", "properties": properties, "required": required}
    if defs:
        parameters["$defs"] = defs

    return FunctionDefinition(
        name=snake_case(workflow_class.__name__),
        description=workflow_class.__doc__,
        parameters=parameters,
    )


def compile_workflow_deployment_function_definition(
    deployment_config: Dict[str, str],
    vellum_client: Vellum,
) -> FunctionDefinition:
    """
    Converts a deployment workflow config into our Vellum-native FunctionDefinition type.

    Args:
        deployment_config: Dict with 'deployment' and 'release_tag' keys
        vellum_client: Vellum client instance
    """
    deployment = deployment_config["deployment"]
    release_tag = deployment_config["release_tag"]

    workflow_deployment_release = vellum_client.release_reviews.retrieve_workflow_deployment_release(
        deployment, release_tag
    )

    input_variables = workflow_deployment_release.workflow_version.input_variables
    description = workflow_deployment_release.description

    properties = {}
    required = []

    for input_var in input_variables:
        properties[input_var.key] = _compile_workflow_deployment_input(input_var)

        if input_var.required and input_var.default is None:
            required.append(input_var.key)

    parameters = {"type": "object", "properties": properties, "required": required}

    return FunctionDefinition(
        name=deployment.replace("-", ""),
        description=description,
        parameters=parameters,
    )
