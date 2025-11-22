import dataclasses
from datetime import datetime
import inspect
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ForwardRef,
    List,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel, TypeAdapter
from pydash import snake_case

from vellum import Vellum
from vellum.client.types.function_definition import FunctionDefinition
from vellum.workflows.integrations.composio_service import ComposioService
from vellum.workflows.integrations.mcp_service import MCPService
from vellum.workflows.integrations.vellum_integration_service import VellumIntegrationService
from vellum.workflows.types.core import is_json_type
from vellum.workflows.types.definition import (
    ComposioToolDefinition,
    DeploymentDefinition,
    MCPServer,
    MCPToolDefinition,
    VellumIntegrationToolDefinition,
)
from vellum.workflows.utils.vellum_variables import vellum_variable_type_to_openapi_type

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow


def _get_def_name(annotation: Type) -> str:
    return f"{annotation.__module__}.{annotation.__qualname__}"


def _strip_titles(value: Any) -> Any:
    """Recursively remove 'title' keys from a schema dictionary."""
    if isinstance(value, dict):
        return {k: _strip_titles(v) for k, v in value.items() if k != "title"}
    if isinstance(value, list):
        return [_strip_titles(v) for v in value]
    return value


def compile_annotation(annotation: Optional[Any], defs: dict[str, Any]) -> dict:
    # Handle special cases that TypeAdapter doesn't handle well
    if annotation is None:
        return {"type": "null"}

    if annotation is Any:
        return {}

    if annotation is datetime:
        return {"type": "string", "format": "date-time"}

    if get_origin(annotation) is Union and is_json_type(get_args(annotation)):
        return {"$ref": "#/$defs/vellum.workflows.types.core.Json"}

    if type(annotation) is ForwardRef:
        # Ignore forward references for now
        return {}

    # Use Pydantic's TypeAdapter for everything else
    try:
        schema = TypeAdapter(annotation).json_schema()
        schema = _strip_titles(schema)

        # Merge any nested $defs into the top-level defs dict
        if "$defs" in schema:
            nested_defs = schema.pop("$defs")
            defs.update(nested_defs)

        return schema
    except Exception as exc:
        raise ValueError(f"Failed to compile schema for annotation {annotation!r}") from exc


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

    Args:
        function: The Python function to compile
    """

    try:
        signature = inspect.signature(function)
    except ValueError as e:
        raise ValueError(f"Failed to get signature for function {function.__name__}: {str(e)}")

    # Get inputs from the decorator if present
    inputs = getattr(function, "__vellum_inputs__", {})
    exclude_params = set(inputs.keys())

    properties = {}
    required = []
    defs: dict[str, Any] = {}
    for param in signature.parameters.values():
        # Skip parameters that are in the exclude_params set
        if exclude_params and param.name in exclude_params:
            continue

        # Check if parameter uses Annotated type hint
        if get_origin(param.annotation) is Annotated:
            args = get_args(param.annotation)
            actual_type = args[0]
            # Extract description from metadata
            description = args[1] if len(args) > 1 and isinstance(args[1], str) else None

            properties[param.name] = compile_annotation(actual_type, defs)
            if description:
                properties[param.name]["description"] = description
        else:
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
    deployment_definition: DeploymentDefinition,
    vellum_client: Vellum,
) -> FunctionDefinition:
    """
    Converts a deployment workflow config into our Vellum-native FunctionDefinition type.

    Args:
        deployment_definition: DeploymentDefinition instance
        vellum_client: Vellum client instance
    """
    release_info = deployment_definition.get_release_info(vellum_client)

    name = release_info["name"]
    description = release_info["description"]
    input_variables = release_info["input_variables"]

    properties = {}
    required = []

    for input_var in input_variables:
        properties[input_var.key] = _compile_workflow_deployment_input(input_var)

        if input_var.required and input_var.default is None:
            required.append(input_var.key)

    parameters = {"type": "object", "properties": properties, "required": required}

    return FunctionDefinition(
        name=name.replace("-", ""),
        description=description,
        parameters=parameters,
    )


def get_mcp_tool_name(tool_def: MCPToolDefinition) -> str:
    """Generate a unique name for an MCP tool by combining server and tool names."""
    server_name = snake_case(tool_def.server.name)
    return f"{server_name}__{tool_def.name}"


def compile_mcp_tool_definition(server_def: MCPServer) -> List[MCPToolDefinition]:
    """Hydrate an MCPToolDefinition with detailed information from the MCP server.

    We do tool discovery on the MCP server to get the tool definitions.

    Args:
        server_def: The basic MCPToolDefinition to enhance

    Returns:
        MCPToolDefinition with detailed parameters and description
    """
    try:
        mcp_service = MCPService()
        return mcp_service.hydrate_tool_definitions(server_def)
    except Exception:
        return []


def compile_composio_tool_definition(tool_def: ComposioToolDefinition) -> FunctionDefinition:
    """Hydrate a ComposioToolDefinition with detailed information from the Composio API.

    Args:
        tool_def: The basic ComposioToolDefinition to enhance

    Returns:
        FunctionDefinition with detailed parameters and description
    """
    try:
        composio_service = ComposioService()
        tool_details = composio_service.get_tool_by_slug(tool_def.action)

        # Create a FunctionDefinition directly with proper field extraction
        return FunctionDefinition(
            name=tool_def.name,
            description=tool_details.get("description", tool_def.description),
            parameters=tool_details.get("input_parameters", {}),
        )
    except Exception:
        # If hydration fails (including no API key), return basic function definition
        return FunctionDefinition(
            name=tool_def.name,
            description=tool_def.description,
            parameters={},
        )


def compile_vellum_integration_tool_definition(
    tool_def: VellumIntegrationToolDefinition,
    vellum_client: Vellum,
) -> FunctionDefinition:
    """Compile a VellumIntegrationToolDefinition into a FunctionDefinition.

    Args:
        tool_def: The VellumIntegrationToolDefinition to compile
        vellum_client: Vellum client instance

    Returns:
        FunctionDefinition with tool parameters and description
    """
    try:
        service = VellumIntegrationService(vellum_client)
        tool_details = service.get_tool_definition(
            integration=tool_def.integration_name,
            provider=tool_def.provider.value,
            tool_name=tool_def.name,
        )

        return FunctionDefinition(
            name=tool_def.name,
            description=tool_details.description,
            parameters=tool_details.parameters or {},
        )
    except Exception:
        # Fallback for service failures
        return FunctionDefinition(name=tool_def.name, description=tool_def.description, parameters={})


def use_tool_inputs(**inputs):
    """
    Decorator to specify which parameters of a tool function should be provided
    from the parent workflow inputs rather than from the LLM.

    Args:
        **inputs: Mapping of parameter names to parent input references

    Example:
        @use_tool_inputs(
            parent_input=ParentInputs.parent_input,
        )
        def get_string(parent_input: str, user_query: str) -> str:
            return f"Parent: {parent_input}, Query: {user_query}"
    """

    def decorator(func: Callable) -> Callable:
        # Store the inputs mapping on the function for later use
        setattr(func, "__vellum_inputs__", inputs)
        return func

    return decorator
