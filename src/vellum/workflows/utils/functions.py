import dataclasses
from datetime import datetime
from enum import Enum
import inspect
import sys
import types
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ForwardRef,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from typing_extensions import TypeGuard

from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from pydash import snake_case

from vellum import Vellum
from vellum.client.types.array_chat_message_content_item import ArrayChatMessageContentItem
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.prompt_output import PromptOutput
from vellum.workflows.constants import undefined
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
    from vellum.workflows.state.context import WorkflowContext
    from vellum.workflows.workflows.base import BaseWorkflow

type_map: dict[Any, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
    None: "null",
    type(None): "null",
    inspect._empty: "null",
    "None": "null",
}

for k, v in list(type_map.items()):
    if isinstance(k, type):
        type_map[k.__name__] = v


def _get_def_name(annotation: Type) -> str:
    return f"{annotation.__module__}.{annotation.__qualname__}"


def is_workflow_context_type(annotation: Any) -> TypeGuard["WorkflowContext"]:
    """Check if the annotation is a WorkflowContext type.

    We check by module and class name to avoid circular imports.
    """
    if annotation is None:
        return False

    # Handle Annotated types by extracting the actual type
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        if args:
            annotation = args[0]

    # Check by module and class name to avoid circular imports
    if hasattr(annotation, "__module__") and hasattr(annotation, "__name__"):
        return annotation.__module__ == "vellum.workflows.state.context" and annotation.__name__ == "WorkflowContext"

    return False


recorded_unions = {
    ArrayChatMessageContentItem: "vellum.client.types.array_chat_message_content_item.ArrayChatMessageContentItem",
    PromptOutput: "vellum.client.types.prompt_output.PromptOutput",
}


def compile_annotation(annotation: Optional[Any], defs: dict[str, Any]) -> dict:
    if annotation is None:
        return {"type": "null"}

    if annotation is Any:
        return {}

    # Handle type variables (e.g., MapNodeItemType) - return empty schema since we can't determine the type
    if isinstance(annotation, TypeVar):
        return {}

    if annotation is datetime:
        return {"type": "string", "format": "date-time"}

    # Handle both typing.Union and PEP 604 union types (str | None on Python 3.10+)
    # On Python 3.10+, get_origin(str | None) returns types.UnionType, not typing.Union
    is_typing_union = get_origin(annotation) is Union
    is_pep604_union = sys.version_info >= (3, 10) and isinstance(annotation, types.UnionType)

    if is_typing_union or is_pep604_union:
        if is_json_type(get_args(annotation)):
            return {"$ref": "#/$defs/vellum.workflows.types.core.Json"}

        if annotation in recorded_unions:
            return {"$ref": f"#/$defs/{recorded_unions[annotation]}"}

        # Filter out Type[undefined] from union args - it just makes the property optional
        filtered_args = [
            a
            for a in get_args(annotation)
            if not (get_origin(a) is type and get_args(a) and get_args(a)[0] is undefined)
        ]

        if len(filtered_args) == 0:
            # Edge case: all union members were Type[undefined], return empty schema
            return {}

        if len(filtered_args) == 1:
            return compile_annotation(filtered_args[0], defs)

        return {"anyOf": [compile_annotation(a, defs) for a in filtered_args]}

    if get_origin(annotation) is Literal:
        values = list(get_args(annotation))
        value_types = {type(value) for value in values}
        if len(value_types) == 1:
            value_type = value_types.pop()
            if value_type in type_map:
                return {"type": type_map[value_type], "enum": values}
            else:
                return {"enum": values}
        else:
            return {"enum": values}

    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        values = [member.value for member in annotation]
        value_types = {type(value) for value in values}
        if len(value_types) == 1:
            value_type = value_types.pop()
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

    if get_origin(annotation) is tuple:
        args = get_args(annotation)
        if len(args) == 2 and args[1] is Ellipsis:
            # Tuple[int, ...] with homogeneous items
            return {"type": "array", "items": compile_annotation(args[0], defs)}
        else:
            # Tuple[int, str] with fixed length items
            result = {
                "type": "array",
                "prefixItems": [compile_annotation(arg, defs) for arg in args],
                "minItems": len(args),
                "maxItems": len(args),
            }
            return result

    if dataclasses.is_dataclass(annotation) and isinstance(annotation, type):
        def_name = _get_def_name(annotation)
        if def_name not in defs:
            properties = {}
            required = []
            for field in dataclasses.fields(annotation):
                properties[field.name] = compile_annotation(field.type, defs)
                if field.default is dataclasses.MISSING:
                    required.append(field.name)
                else:
                    properties[field.name]["default"] = _compile_default_value(field.default)
            defs[def_name] = {"type": "object", "properties": properties, "required": required}
        return {"$ref": f"#/$defs/{def_name}"}

    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        def_name = _get_def_name(annotation)
        if def_name not in defs:
            properties = {}
            required = []
            for field_name, field_info in annotation.model_fields.items():
                # field_info is a FieldInfo object which has an annotation attribute
                properties[field_name] = compile_annotation(field_info.annotation, defs)

                if field_info.description is not None:
                    properties[field_name]["description"] = field_info.description

                if field_info.default is PydanticUndefined:
                    required.append(field_name)
                else:
                    properties[field_name]["default"] = _compile_default_value(field_info.default)
            defs[def_name] = {"type": "object", "properties": properties, "required": required}

        return {"$ref": f"#/$defs/{def_name}"}

    if type(annotation) is ForwardRef:
        # Ignore forward references for now
        return {}

    # Handle Type[undefined] - skip it as it just makes the property optional
    if get_origin(annotation) is type:
        args = get_args(annotation)
        if args and args[0] is undefined:
            return {}

    # Handle regular classes with __init__ methods by inspecting their constructor signature
    if inspect.isclass(annotation) and hasattr(annotation, "__init__"):
        try:
            init_signature = inspect.signature(annotation.__init__)
            init_params = list(init_signature.parameters.values())
            # Skip 'self' parameter and *args/**kwargs
            init_params = [
                p
                for p in init_params
                if p.name != "self" and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            ]

            # Only process if there are typed parameters
            if init_params and any(p.annotation is not inspect.Parameter.empty for p in init_params):
                def_name = _get_def_name(annotation)
                if def_name not in defs:
                    properties = {}
                    required = []
                    for param in init_params:
                        if param.annotation is not inspect.Parameter.empty:
                            properties[param.name] = compile_annotation(param.annotation, defs)
                            if param.default is inspect.Parameter.empty:
                                required.append(param.name)
                            else:
                                properties[param.name]["default"] = _compile_default_value(param.default)
                    defs[def_name] = {"type": "object", "properties": properties, "required": required}
                return {"$ref": f"#/$defs/{def_name}"}
        except (ValueError, TypeError):
            # If we can't inspect the signature, fall through to the error
            pass

    if annotation not in type_map:
        raise ValueError(f"Failed to compile type: {annotation}")

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

    Args:
        function: The Python function to compile
    """

    try:
        signature = inspect.signature(function)
    except ValueError as e:
        raise ValueError(f"Failed to get signature for function {function.__name__}: {str(e)}")

    # Get inputs from the decorator if present
    inputs = getattr(function, "__vellum_inputs__", {})
    examples = getattr(function, "__vellum_examples__", None)
    exclude_params = set(inputs.keys())

    properties = {}
    required = []
    defs: dict[str, Any] = {}
    for param in signature.parameters.values():
        # Skip parameters that are in the exclude_params set
        if exclude_params and param.name in exclude_params:
            continue

        # Skip WorkflowContext parameters - they are provided by the runtime, not the LLM
        if is_workflow_context_type(param.annotation):
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
    if examples is not None:
        parameters["examples"] = examples

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

    # Get inputs from the decorator if present (to exclude from schema)
    inputs = getattr(workflow_class, "__vellum_inputs__", {})
    examples = getattr(workflow_class, "__vellum_examples__", None)
    exclude_params = set(inputs.keys())

    properties = {}
    required = []
    defs: dict[str, Any] = {}

    for name, field_type in inputs_class.__annotations__.items():
        if name.startswith("__"):
            continue

        # Skip parameters that are in the exclude_params set
        if exclude_params and name in exclude_params:
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
    if examples is not None:
        parameters["examples"] = examples

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
            toolkit_version=tool_def.toolkit_version,
        )

        return FunctionDefinition(
            name=tool_def.name,
            description=tool_details.description,
            parameters=tool_details.parameters or {},
        )
    except Exception:
        # Fallback for service failures
        return FunctionDefinition(name=tool_def.name, description=tool_def.description, parameters={})


ToolType = Union[Callable[..., Any], Type["BaseWorkflow"]]


def tool(
    *,
    inputs: Optional[dict[str, Any]] = None,
    examples: Optional[List[dict[str, Any]]] = None,
) -> Callable[[ToolType], ToolType]:
    """
    Decorator to configure a tool function or inline workflow.

    Currently supports specifying which parameters should come from parent workflow inputs
    via the `inputs` mapping. Also supports providing `examples` which will be hoisted
    into the JSON Schema `examples` keyword for this tool's parameters.

    Args:
        inputs: Mapping of parameter names to parent input references
        examples: List of example argument objects for the tool

    Example with function:
        @tool(inputs={
            "parent_input": ParentInputs.parent_input,
        }, examples=[{"location": "San Francisco"}])
        def get_string(parent_input: str, user_query: str) -> str:
            return f"Parent: {parent_input}, Query: {user_query}"

    Example with inline workflow:
        @tool(inputs={
            "context": ParentInputs.context,
        })
        class MyInlineWorkflow(BaseWorkflow):
            graph = MyNode

            class Outputs(BaseWorkflow.Outputs):
                result = MyNode.Outputs.result
    """

    def decorator(func: ToolType) -> ToolType:
        # Store the inputs mapping on the function/workflow for later use
        if inputs is not None:
            setattr(func, "__vellum_inputs__", inputs)
        # Store the examples on the function/workflow for later use
        if examples is not None:
            setattr(func, "__vellum_examples__", examples)
        return func

    return decorator


def use_tool_inputs(**inputs: Any) -> Callable[[Callable], Callable]:
    """
    Decorator to specify which parameters of a tool function should be provided
    from the parent workflow inputs rather than from the LLM.

    .. deprecated:: 2.0.0
        This function is deprecated and will be removed in version 2.0.0.
        Use :func:`tool` with the ``inputs`` parameter instead.

    This is a backward-compatible helper equivalent to @tool(inputs={...}).

    Args:
        **inputs: Mapping of parameter names to parent input references

    Example:
        @use_tool_inputs(
            parent_input=ParentInputs.parent_input,
        )
        def get_string(parent_input: str, user_query: str) -> str:
            return f"Parent: {parent_input}, Query: {user_query}"
    """
    return tool(inputs=inputs)
