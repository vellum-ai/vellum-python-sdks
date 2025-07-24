import json
import logging
import os
from typing import Any, Callable, Iterator, List, Optional, Type, cast

from pydash import snake_case

from vellum import ChatMessage, PromptBlock
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_parameters import PromptParameters
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.expressions.concat import ConcatExpression
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.displayable.subworkflow_deployment_node.node import SubworkflowDeploymentNode
from vellum.workflows.nodes.displayable.tool_calling_node.composio_service import ComposioService
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state import BaseState
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.core import EntityInputsInterface, MergeBehavior, Tool
from vellum.workflows.types.definition import ComposioToolDefinition, DeploymentDefinition
from vellum.workflows.types.generics import is_workflow_class

logger = logging.getLogger(__name__)

CHAT_HISTORY_VARIABLE = "chat_history"


class FunctionCallNodeMixin:
    """Mixin providing common functionality for nodes that handle function calls."""

    function_call_output: List[PromptOutput]

    def _extract_function_arguments(self) -> dict:
        """Extract arguments from function call output."""
        if self.function_call_output and len(self.function_call_output) > 0:
            function_call = self.function_call_output[0]
            if function_call.type == "FUNCTION_CALL" and function_call.value is not None:
                arguments = function_call.value.arguments or {}

                # Handle double-encoded arguments with kwargs wrapper (common with Composio tools)
                if isinstance(arguments, dict) and "kwargs" in arguments and len(arguments) == 1:
                    kwargs_value = arguments["kwargs"]
                    if isinstance(kwargs_value, str):
                        try:
                            # Parse JSON-stringified kwargs
                            parsed_kwargs = json.loads(kwargs_value)
                            if isinstance(parsed_kwargs, dict):
                                return parsed_kwargs
                        except (json.JSONDecodeError, TypeError):
                            # If parsing fails, fall back to original arguments
                            pass

                return arguments
        return {}

    def _add_function_result_to_chat_history(self, result: Any, state: ToolCallingState) -> None:
        """Add function execution result to chat history."""
        state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=json.dumps(result, cls=DefaultStateEncoder)),
            )
        )


class ToolRouterNode(InlinePromptNode[ToolCallingState]):
    max_prompt_iterations: Optional[int] = 5

    class Trigger(InlinePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES

    def run(self) -> Iterator[BaseOutput]:
        logger.info("=" * 80)
        logger.info("TOOL ROUTER NODE EXECUTION STARTED")
        logger.info("=" * 80)
        logger.info(f"Current prompt iterations: {self.state.prompt_iterations}")
        logger.info(f"Max prompt iterations: {self.max_prompt_iterations}")

        if self.state.prompt_iterations >= self.max_prompt_iterations:
            max_iterations_message = f"Maximum number of prompt iterations `{self.max_prompt_iterations}` reached."
            logger.error(f"Max iterations reached: {max_iterations_message}")
            raise NodeException(message=max_iterations_message, code=WorkflowErrorCode.NODE_EXECUTION)

        logger.info("Calling parent InlinePromptNode.run()...")
        generator = super().run()
        for output in generator:
            logger.info(f"ToolRouterNode received output: name='{output.name}', value_type={type(output.value)}")

            if output.name == "results" and output.value:
                values = cast(List[Any], output.value)
                logger.info(f"Processing results output with {len(values)} values")

                if values and len(values) > 0:
                    logger.info(f"First result type: {values[0].type}")

                    if values[0].type == "STRING":
                        logger.info(f"Processing STRING result: {values[0].value[:100]}...")
                        self.state.chat_history.append(ChatMessage(role="ASSISTANT", text=values[0].value))

                    elif values[0].type == "FUNCTION_CALL":
                        logger.info("Processing FUNCTION_CALL result")
                        self.state.prompt_iterations += 1
                        logger.info(f"Incremented prompt iterations to: {self.state.prompt_iterations}")

                        function_call = values[0].value
                        if function_call is not None:
                            logger.info(f"Function call details:")
                            logger.info(f"  - Name: {function_call.name}")
                            logger.info(f"  - ID: {function_call.id}")
                            logger.info(f"  - State: {getattr(function_call, 'state', 'NOT_SET')}")
                            logger.info(f"  - Arguments: {function_call.arguments}")

                            self.state.chat_history.append(
                                ChatMessage(
                                    role="ASSISTANT",
                                    content=FunctionCallChatMessageContent(
                                        value=FunctionCallChatMessageContentValue(
                                            name=function_call.name,
                                            arguments=function_call.arguments,
                                            id=function_call.id,
                                        ),
                                    ),
                                )
                            )
                            logger.info("Added function call to chat history")
            yield output


class DynamicSubworkflowDeploymentNode(SubworkflowDeploymentNode[ToolCallingState], FunctionCallNodeMixin):
    """Node that executes a deployment definition with function call output."""

    def run(self) -> Iterator[BaseOutput]:
        arguments = self._extract_function_arguments()

        # Mypy doesn't like instance assignments of class attributes. It's safe in our case tho bc it's what
        # we do in the `__init__` method. Long term, instead of the function_call_output attribute above, we
        # want to do:
        # ```python
        # subworkflow_inputs = tool_router_node.Outputs.results[0]['value']['arguments'].if_(
        #     tool_router_node.Outputs.results[0]['type'].equals('FUNCTION_CALL'),
        #     {},
        # )
        # ```
        self.subworkflow_inputs = arguments  # type:ignore[misc]

        # Call the parent run method to execute the subworkflow
        outputs = {}
        for output in super().run():
            if output.is_fulfilled:
                outputs[output.name] = output.value
            yield output

        # Add the result to the chat history
        self._add_function_result_to_chat_history(outputs, self.state)


class DynamicInlineSubworkflowNode(
    InlineSubworkflowNode[ToolCallingState, BaseInputs, BaseState], FunctionCallNodeMixin
):
    """Node that executes an inline subworkflow with function call output."""

    def run(self) -> Iterator[BaseOutput]:
        arguments = self._extract_function_arguments()

        self.subworkflow_inputs = arguments  # type: ignore[misc]

        # Call the parent run method to execute the subworkflow with proper streaming
        outputs = {}

        for output in super().run():
            if output.is_fulfilled:
                outputs[output.name] = output.value
            yield output

        # Add the result to the chat history
        self._add_function_result_to_chat_history(outputs, self.state)


class FunctionNode(BaseNode[ToolCallingState], FunctionCallNodeMixin):
    """Node that executes a regular Python function with function call output."""

    function_definition: Callable[..., Any]

    def run(self) -> Iterator[BaseOutput]:
        arguments = self._extract_function_arguments()

        try:
            result = self.function_definition(**arguments)
        except Exception as e:
            function_name = self.function_definition.__name__
            raise NodeException(
                message=f"Error executing function '{function_name}': {str(e)}",
                code=WorkflowErrorCode.NODE_EXECUTION,
            )

        # Add the result to the chat history
        self._add_function_result_to_chat_history(result, self.state)

        yield from []


class ComposioNode(BaseNode[ToolCallingState], FunctionCallNodeMixin):
    """Node that executes a Composio tool with function call output."""

    composio_tool: ComposioToolDefinition

    def run(self) -> Iterator[BaseOutput]:
        logger.info("!" * 80)
        logger.info("COMPOSIO NODE EXECUTION STARTED")
        logger.info("!" * 80)
        logger.info(f"Composio tool: {self.composio_tool.action}")
        logger.info(f"Tool name: {self.composio_tool.name}")
        logger.info(f"Function call output available: {hasattr(self, 'function_call_output')}")

        if hasattr(self, "function_call_output"):
            logger.info(f"Function call output length: {len(self.function_call_output)}")
            if self.function_call_output:
                logger.info(f"First function call output type: {self.function_call_output[0].type}")

        # Extract arguments from function call
        logger.info("Extracting function arguments...")
        arguments = self._extract_function_arguments()
        logger.info(f"Extracted arguments: {arguments}")

        # HACK: Use first Composio API key found in environment variables
        composio_api_key = None
        common_env_var_names = ["COMPOSIO_API_KEY", "COMPOSIO_KEY"]
        logger.info("Searching for Composio API key...")

        for env_var_name in common_env_var_names:
            value = os.environ.get(env_var_name)
            logger.info(f"Checking {env_var_name}: {'SET' if value else 'NOT_SET'}")
            if value:
                composio_api_key = value
                logger.info(f"Found API key in {env_var_name}")
                break

        if not composio_api_key:
            logger.error("No Composio API key found!")
            raise NodeException(
                message=(
                    "No Composio API key found in environment variables. "
                    "Please ensure one of these environment variables is set: "
                )
                + ", ".join(common_env_var_names),
                code=WorkflowErrorCode.NODE_EXECUTION,
            )

        try:
            # Execute using ComposioService
            logger.info(f"Creating ComposioService with API key (length: {len(composio_api_key)})...")
            composio_service = ComposioService(api_key=composio_api_key)
            logger.info("ComposioService created successfully")

            # Get all user connections and find matching one for the toolkit
            logger.info("Getting user connections to find matching connection...")
            connections = composio_service.get_user_connections()
            matching_connection = None

            for connection in connections:
                logger.info(f"Checking connection: {connection.integration_name} (status: {connection.status})")
                if (
                    connection.integration_name.upper() == self.composio_tool.toolkit.upper()
                    and connection.status == "ACTIVE"
                ):
                    matching_connection = connection
                    logger.info(f"Found matching active connection: {connection.connection_id}")
                    break

            if not matching_connection:
                logger.error(f"No active connection found for toolkit '{self.composio_tool.toolkit}'")
                raise NodeException(
                    message=f"No active connection found for toolkit '{self.composio_tool.toolkit}'. Please ensure you have an active connection for this integration.",
                    code=WorkflowErrorCode.NODE_EXECUTION,
                )

            logger.info(
                f"Calling composio_service.execute_tool(tool_name='{self.composio_tool.action}', arguments={arguments}, connection_id='{matching_connection.connection_id}')"
            )
            result = composio_service.execute_tool(
                tool_name=self.composio_tool.action,
                arguments=arguments,
                connection_id=matching_connection.connection_id,
            )
            logger.info(f"ComposioService.execute_tool returned: {result}")

        except Exception as e:
            logger.error(f"Exception during Composio tool execution: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            raise NodeException(
                message=f"Error executing Composio tool '{self.composio_tool.action}': {str(e)}",
                code=WorkflowErrorCode.NODE_EXECUTION,
            )

        # Add result to chat history
        logger.info("Adding result to chat history...")
        self._add_function_result_to_chat_history(result, self.state)
        logger.info("COMPOSIO NODE EXECUTION COMPLETED")
        logger.info("!" * 80)

        yield from []


def get_composio_api_key() -> str:
    """Get the Composio API key from configuration

    This retrieves the API key from environment variables.
    Could be extended to support other configuration sources.
    """
    api_key = os.environ.get("COMPOSIO_API_KEY") or os.environ.get("COMPOSIO_KEY")
    if not api_key:
        raise ValueError("COMPOSIO_API_KEY or COMPOSIO_KEY environment variable not set")
    return api_key


def create_parameter_definition_from_composio(param_name: str, param_info: dict) -> dict:
    """Create a parameter definition from Composio parameter info

    Args:
        param_name: Name of the parameter
        param_info: Parameter information from Composio schema

    Returns:
        Parameter definition dict compatible with OpenAPI spec
    """
    # Map Composio types to OpenAPI types
    type_mapping = {
        "string": "string",
        "boolean": "boolean",
        "number": "number",
        "integer": "integer",
        "array": "array",
        "object": "object",
    }

    param_type = type_mapping.get(param_info.get("type", "string"), "string")

    param_def = {
        "type": param_type,
        "description": param_info.get("description", ""),
    }

    # Add default value if present
    if "default" in param_info:
        param_def["default"] = param_info["default"]

    # Handle array item types if specified
    if param_type == "array" and "items" in param_info:
        param_def["items"] = param_info["items"]

    # Handle object properties if specified
    if param_type == "object" and "properties" in param_info:
        param_def["properties"] = param_info["properties"]
        if "required" in param_info:
            param_def["required"] = param_info["required"]

    # Add examples if present
    if "examples" in param_info:
        param_def["examples"] = param_info["examples"]

    return param_def


def create_function_definition_from_composio(
    composio_tool: ComposioToolDefinition, composio_service: ComposioService
) -> FunctionDefinition:
    """Create a FunctionDefinition from ComposioToolDefinition with fresh parameters

    Args:
        composio_tool: The ComposioToolDefinition with basic tool info
        composio_service: Service to fetch fresh parameter schema

    Returns:
        FunctionDefinition populated with tool info and fresh parameters
    """
    logger.info(f"Creating FunctionDefinition for Composio tool: {composio_tool.action}")

    try:
        # Get fresh parameter schema from Composio API
        logger.info(f"Fetching fresh schema for {composio_tool.action}")
        actions = composio_service.core_client.actions.get(actions=[composio_tool.action], limit=1)

        if not actions or len(actions) == 0:
            logger.error(f"Failed to fetch schema for {composio_tool.action}")
            # Fallback to basic definition without parameters
            return FunctionDefinition(
                name=composio_tool.action,
                description=composio_tool.description or f"Composio tool: {composio_tool.name}",
                parameters=None,
            )

        tool_details = actions[0]
        logger.info(f"Retrieved tool details for {composio_tool.action}")

        # Extract parameter information
        input_params = {}
        required_params = []

        if hasattr(tool_details, "parameters") and tool_details.parameters:
            if hasattr(tool_details.parameters, "properties"):
                input_params = tool_details.parameters.properties
            if hasattr(tool_details.parameters, "required"):
                required_params = tool_details.parameters.required or []

        # Convert Composio parameters to OpenAPI parameter schema
        parameter_properties = {}
        for param_name, param_info in input_params.items():
            # Convert param_info to dict if it's not already
            if hasattr(param_info, "__dict__"):
                param_info_dict = param_info.__dict__
            elif hasattr(param_info, "model_dump"):
                param_info_dict = param_info.model_dump()
            else:
                param_info_dict = param_info if isinstance(param_info, dict) else {}

            parameter_properties[param_name] = create_parameter_definition_from_composio(param_name, param_info_dict)

        logger.info(f"Created {len(parameter_properties)} parameter definitions")

        # Create OpenAPI-style parameter schema
        parameters_schema = None
        if parameter_properties:
            parameters_schema = {"type": "object", "properties": parameter_properties, "required": required_params}

        # Create FunctionDefinition with all information
        function_def = FunctionDefinition(
            name=composio_tool.action,  # Use action slug as function name
            description=composio_tool.description or getattr(tool_details, "description", ""),
            parameters=parameters_schema,
        )

        # Store Composio-specific metadata using FunctionDefinition's extra field support
        # The client FunctionDefinition allows extra fields, so we can add metadata
        if hasattr(function_def, "__dict__"):
            function_def.__dict__["composio_metadata"] = {
                "tool_type": "COMPOSIO",
                "tool_slug": composio_tool.action,
                "tool_name": composio_tool.name,
                "toolkit": composio_tool.toolkit,
                "integration_name": getattr(composio_tool, "integration_name", composio_tool.toolkit),
                "version": getattr(tool_details, "version", ""),
            }

        logger.info(f"Successfully created FunctionDefinition for {composio_tool.action}")
        return function_def

    except Exception as e:
        logger.error(f"Error creating FunctionDefinition for {composio_tool.action}: {e}")
        # Return a basic function definition as fallback
        return FunctionDefinition(
            name=composio_tool.action, description=f"Composio tool: {composio_tool.name}", parameters=None
        )


def wrap_composio_tool_as_function(composio_tool: ComposioToolDefinition) -> FunctionDefinition:
    """Wrapper function to convert ComposioToolDefinition to FunctionDefinition

    This function should be called wherever Composio tools need to be converted
    to the standard FunctionDefinition format used by the workflow system.
    """
    try:
        # Initialize ComposioService
        api_key = get_composio_api_key()
        composio_service = ComposioService(api_key)

        return create_function_definition_from_composio(composio_tool, composio_service)

    except Exception as e:
        logger.error(f"Failed to create FunctionDefinition for {composio_tool.action}: {e}")
        # Return fallback FunctionDefinition
        return FunctionDefinition(
            name=composio_tool.action, description=f"Composio tool: {composio_tool.name}", parameters=None
        )


def is_composio_function_definition(function_def: FunctionDefinition) -> bool:
    """Check if a FunctionDefinition represents a Composio tool"""
    if hasattr(function_def, "__dict__") and "composio_metadata" in function_def.__dict__:
        return function_def.__dict__["composio_metadata"].get("tool_type") == "COMPOSIO"
    return False


def get_composio_metadata_from_function_definition(function_def: FunctionDefinition) -> Optional[dict]:
    """Extract Composio metadata from a FunctionDefinition"""
    if hasattr(function_def, "__dict__") and "composio_metadata" in function_def.__dict__:
        return function_def.__dict__["composio_metadata"]
    return None


# Legacy function - updated to use FunctionDefinition approach for consistency
def create_composio_wrapper_function(tool_def: ComposioToolDefinition):
    """Create a real Python function that wraps the Composio tool for prompt layer compatibility."""

    # If no parameters are set, try to fetch them
    if not tool_def.parameters:
        logger.info(f"No parameters found for {tool_def.action}, attempting to fetch schema...")
        try:
            # Get API key from environment
            api_key = os.environ.get("COMPOSIO_API_KEY") or os.environ.get("COMPOSIO_KEY")
            if api_key:
                composio_service = ComposioService(api_key)

                # Fetch the real schema
                actions = composio_service.core_client.actions.get(actions=[tool_def.action], limit=1)
                if actions and len(actions) > 0:
                    tool_details = actions[0]

                    if hasattr(tool_details, "parameters") and tool_details.parameters:
                        param_properties = tool_details.parameters.properties
                        required_params = tool_details.parameters.required

                        # Update the tool definition with real schema
                        tool_def.parameters = {
                            "type": "object",
                            "properties": {},
                            "required": required_params or [],
                        }

                        for param_name, param_info in param_properties.items():
                            tool_def.parameters["properties"][param_name] = {
                                "type": param_info.get("type", "string"),
                                "description": param_info.get("description", ""),
                            }

                        logger.info(
                            f"Updated {tool_def.action} with parameters: {list(tool_def.parameters['properties'].keys())}"
                        )

        except Exception as e:
            logger.warning(f"Could not fetch schema for {tool_def.action}: {e}")

    def wrapper_function(**kwargs):
        # Validate arguments against schema if available
        if tool_def.parameters and not tool_def.validate_arguments(kwargs):
            raise ValueError(f"Invalid arguments for {tool_def.action}: arguments do not match expected schema")

        # This should never be called due to routing, but satisfies introspection
        raise RuntimeError(
            f"ComposioToolDefinition wrapper for '{tool_def.action}' should not be called directly. "
            f"Execution should go through ComposioNode. This suggests a routing issue."
        )

    # Set proper function attributes for prompt layer introspection
    wrapper_function.__name__ = tool_def.name
    wrapper_function.__doc__ = tool_def.description

    # CRITICAL: Set the function schema so the prompt layer can generate correct OpenAI schema
    if hasattr(tool_def, "to_function_definition"):
        wrapper_function._function_definition = tool_def.to_function_definition()

    # Also set parameters directly on the function for prompt layer to use
    wrapper_function._parameters = tool_def.parameters

    # return new FunctionDefinition
    return wrapper_function


def create_tool_router_node(
    ml_model: str,
    blocks: List[PromptBlock],
    functions: List[Tool],
    prompt_inputs: Optional[EntityInputsInterface],
    parameters: PromptParameters,
    max_prompt_iterations: Optional[int] = None,
) -> Type[ToolRouterNode]:
    logger.info("%" * 80)
    logger.info("CREATE TOOL ROUTER NODE CALLED")
    logger.info("%" * 80)
    logger.info(f"ML Model: {ml_model}")
    logger.info(f"Functions count: {len(functions)}")
    logger.info(f"Max prompt iterations: {max_prompt_iterations}")

    if functions and len(functions) > 0:
        # Create dynamic ports and convert functions in a single loop
        Ports = type("Ports", (), {})
        prompt_functions = []
        logger.info("Creating ports for functions...")

        for i, function in enumerate(functions):
            # Convert ComposioToolDefinition to FunctionDefinition for prompt layer
            if isinstance(function, ComposioToolDefinition):
                logger.info(f"  [{i}] Creating FunctionDefinition for ComposioToolDefinition: {function.action}")
                function_def = wrap_composio_tool_as_function(function)
                prompt_functions.append(function_def)
            else:
                logger.info(f"  [{i}] Using regular function: {getattr(function, '__name__', str(function))}")
                prompt_functions.append(function)

            # Create port for this function (using original function for get_function_name)
            function_name = get_function_name(function)
            logger.info(f"  [{i}] Function name for port: {function_name}")

            # Avoid using lambda to capture function_name
            # lambda will capture the function_name by reference,
            # and if the function_name is changed, the port_condition will also change.
            def create_port_condition(fn_name):
                logger.info(f"  Creating port condition for function: {fn_name}")
                return LazyReference(
                    lambda: (
                        node.Outputs.results[0]["type"].equals("FUNCTION_CALL")
                        & node.Outputs.results[0]["value"]["name"].equals(fn_name)
                    )
                )

            port_condition = create_port_condition(function_name)
            port = Port.on_if(port_condition)
            setattr(Ports, function_name, port)
            logger.info(f"  [{i}] Created port '{function_name}' with condition")

        # Add the else port for when no function conditions match
        setattr(Ports, "default", Port.on_else())
        logger.info("Created 'default' port for non-matching cases")
    else:
        # If no functions exist, create a simple Ports class with just a default port
        logger.info("No functions provided, creating simple default port")
        Ports = type("Ports", (), {"default": Port(default=True)})
        prompt_functions = []

    # Add a chat history block to blocks only if one doesn't already exist
    has_chat_history_block = any(
        block.block_type == "VARIABLE" and block.input_variable == CHAT_HISTORY_VARIABLE for block in blocks
    )

    if not has_chat_history_block:
        blocks.append(
            VariablePromptBlock(
                block_type="VARIABLE",
                input_variable=CHAT_HISTORY_VARIABLE,
                state=None,
                cache_config=None,
            )
        )

    node_prompt_inputs = {
        **(prompt_inputs or {}),
        CHAT_HISTORY_VARIABLE: ConcatExpression[List[ChatMessage], List[ChatMessage]](
            lhs=(prompt_inputs or {}).get(CHAT_HISTORY_VARIABLE, []),
            rhs=ToolCallingState.chat_history,
        ),
    }

    node = cast(
        Type[ToolRouterNode],
        type(
            "ToolRouterNode",
            (ToolRouterNode,),
            {
                "ml_model": ml_model,
                "blocks": blocks,
                "functions": prompt_functions,  # Use converted functions for prompt layer
                "prompt_inputs": node_prompt_inputs,
                "parameters": parameters,
                "max_prompt_iterations": max_prompt_iterations,
                "Ports": Ports,
                "__module__": __name__,
            },
        ),
    )
    return node


def create_function_node(
    function: Tool,
    tool_router_node: Type[ToolRouterNode],
) -> Type[BaseNode]:
    """
    Create a FunctionNode class for a given function.

    For workflow functions: BaseNode
    For regular functions: BaseNode with direct function call
    For Composio FunctionDefinitions: ComposioNode with extracted metadata

    Args:
        function: The function to create a node for
        tool_router_node: The tool router node class
    """
    logger.info("^" * 80)
    logger.info("CREATE FUNCTION NODE CALLED")
    logger.info("^" * 80)
    logger.info(f"Function type: {type(function).__name__}")

    # Check if this is a FunctionDefinition representing a Composio tool
    if isinstance(function, FunctionDefinition) and is_composio_function_definition(function):
        logger.info("Detected Composio FunctionDefinition, creating ComposioNode...")
        composio_metadata = get_composio_metadata_from_function_definition(function)

        if composio_metadata:
            # Reconstruct ComposioToolDefinition from metadata
            composio_tool = ComposioToolDefinition(
                toolkit=composio_metadata["toolkit"],
                action=composio_metadata["tool_slug"],
                description=function.description or f"Composio tool: {composio_metadata['tool_name']}",
                display_name=composio_metadata["tool_name"],
                parameters=function.parameters,
            )

            logger.info(f"Reconstructed ComposioToolDefinition: {composio_tool.action}")

            node_name = f"ComposioNode_{composio_tool.name}"
            logger.info(f"Creating dynamic ComposioNode class: {node_name}")

            node = type(
                node_name,
                (ComposioNode,),
                {
                    "composio_tool": composio_tool,
                    "function_call_output": tool_router_node.Outputs.results,
                    "__module__": __name__,
                },
            )
            logger.info(f"Created ComposioNode from FunctionDefinition: {node}")
            logger.info("^" * 80)
            return node
        else:
            logger.warning(
                "Could not extract Composio metadata from FunctionDefinition, treating as regular FunctionDefinition"
            )
            # Fall through to regular FunctionDefinition handling

    if isinstance(function, DeploymentDefinition):
        logger.info("Creating DynamicSubworkflowDeploymentNode...")
        deployment = function.deployment_id or function.deployment_name
        release_tag = function.release_tag
        logger.info(f"Deployment: {deployment}, Release tag: {release_tag}")

        node = type(
            f"DynamicSubworkflowDeploymentNode_{deployment}",
            (DynamicSubworkflowDeploymentNode,),
            {
                "deployment": deployment,
                "release_tag": release_tag,
                "function_call_output": tool_router_node.Outputs.results,
                "__module__": __name__,
            },
        )
        logger.info(f"Created DynamicSubworkflowDeploymentNode: {node}")
        return node

    elif isinstance(function, ComposioToolDefinition):
        logger.info("Creating ComposioNode...")
        logger.info(f"ComposioToolDefinition action: {function.action}")
        logger.info(f"ComposioToolDefinition name: {function.name}")

        node_name = f"ComposioNode_{function.name}"
        logger.info(f"Creating dynamic class: {node_name}")

        node = type(
            node_name,
            (ComposioNode,),
            {
                "composio_tool": function,
                "function_call_output": tool_router_node.Outputs.results,
                "__module__": __name__,
            },
        )
        logger.info(f"Created ComposioNode: {node}")
        logger.info(f"ComposioNode class attributes: composio_tool={getattr(node, 'composio_tool', 'NOT_SET')}")
        logger.info("^" * 80)
        return node
    elif is_workflow_class(function):
        logger.info("Creating DynamicInlineSubworkflowNode...")
        node = type(
            f"DynamicInlineSubworkflowNode_{function.__name__}",
            (DynamicInlineSubworkflowNode,),
            {
                "subworkflow": function,
                "function_call_output": tool_router_node.Outputs.results,
                "__module__": __name__,
            },
        )
        logger.info(f"Created DynamicInlineSubworkflowNode: {node}")
        return node
    elif isinstance(function, FunctionDefinition):
        # For non-Composio FunctionDefinition objects, create a simple function node
        logger.info("Creating FunctionNode for FunctionDefinition...")
        function_name = function.name or "unknown_function"

        def function_wrapper(**kwargs):
            raise RuntimeError(f"FunctionDefinition '{function_name}' cannot be executed directly")

        node = type(
            f"FunctionNode_{function_name}",
            (FunctionNode,),
            {
                "function_definition": function_wrapper,
                "function_call_output": tool_router_node.Outputs.results,
                "__module__": __name__,
            },
        )
        logger.info(f"Created FunctionNode for FunctionDefinition: {node}")
        return node
    else:
        # For regular functions, use FunctionNode
        logger.info("Creating FunctionNode for regular function...")
        if callable(function):
            node = type(
                f"FunctionNode_{function.__name__}",
                (FunctionNode,),
                {
                    "function_definition": lambda self, **kwargs: function(**kwargs),
                    "function_call_output": tool_router_node.Outputs.results,
                    "__module__": __name__,
                },
            )
            logger.info(f"Created FunctionNode: {node}")
            return node
        else:
            logger.error(f"Cannot create function node for non-callable object: {function}")
            raise ValueError(f"Cannot create function node for non-callable object: {function}")


def get_function_name(function: Tool) -> str:
    if isinstance(function, DeploymentDefinition):
        name = str(function.deployment_id or function.deployment_name)
        return name.replace("-", "")
    elif isinstance(function, ComposioToolDefinition):
        return function.name
    elif isinstance(function, FunctionDefinition):
        # For FunctionDefinition objects, use the name directly
        return function.name or "unknown_function"
    else:
        return snake_case(function.__name__)
