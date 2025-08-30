import json
import logging
from typing import Any, Callable, Dict, Iterator, List, Optional, Type, Union, cast

from pydash import snake_case

from vellum import ChatMessage, PromptBlock
from vellum.client.types.array_chat_message_content import ArrayChatMessageContent
from vellum.client.types.array_chat_message_content_item import ArrayChatMessageContentItem
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
from vellum.workflows.integrations.composio_service import ComposioService
from vellum.workflows.integrations.mcp_service import MCPService
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.displayable.subworkflow_deployment_node.node import SubworkflowDeploymentNode
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.ports.port import Port
from vellum.workflows.state import BaseState
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.core import EntityInputsInterface, MergeBehavior, Tool, ToolBase
from vellum.workflows.types.definition import ComposioToolDefinition, DeploymentDefinition, MCPServer, MCPToolDefinition
from vellum.workflows.types.generics import is_workflow_class

CHAT_HISTORY_VARIABLE = "chat_history"


logger = logging.getLogger(__name__)


class FunctionCallNodeMixin:
    """Mixin providing common functionality for nodes that handle function calls."""

    function_call_output: List[PromptOutput]

    def _extract_function_arguments(self) -> dict:
        """Extract arguments from function call output."""
        current_index = getattr(self, "state").current_prompt_output_index
        if self.function_call_output and len(self.function_call_output) > current_index:
            function_call = self.function_call_output[current_index]
            if function_call.type == "FUNCTION_CALL" and function_call.value is not None:
                return function_call.value.arguments or {}
        return {}

    def _extract_function_call_id(self) -> Optional[str]:
        """Extract function call ID from function call output."""
        current_index = getattr(self, "state").current_prompt_output_index
        if self.function_call_output and len(self.function_call_output) > current_index:
            function_call = self.function_call_output[current_index]
            if function_call.type == "FUNCTION_CALL" and function_call.value is not None:
                return function_call.value.id
        return None

    def _add_function_result_to_chat_history(self, result: Any, state: ToolCallingState) -> None:
        """Add function execution result to chat history."""
        function_call_id = self._extract_function_call_id()
        state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=json.dumps(result, cls=DefaultStateEncoder)),
                source=function_call_id,
            )
        )
        with state.__quiet__():
            state.current_function_calls_processed += 1
            state.current_prompt_output_index += 1


class ToolPromptNode(InlinePromptNode[ToolCallingState]):
    max_prompt_iterations: Optional[int] = 5

    class Trigger(InlinePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES

    def run(self) -> Iterator[BaseOutput]:
        if self.max_prompt_iterations is not None and self.state.prompt_iterations >= self.max_prompt_iterations:
            max_iterations_message = f"Maximum number of prompt iterations `{self.max_prompt_iterations}` reached."
            raise NodeException(message=max_iterations_message, code=WorkflowErrorCode.NODE_EXECUTION)

        generator = super().run()
        with self.state.__quiet__():
            self.state.current_prompt_output_index = 0
            self.state.current_function_calls_processed = 0
            self.state.prompt_iterations += 1
        for output in generator:
            if output.name == InlinePromptNode.Outputs.results.name and output.value:
                prompt_outputs = cast(List[PromptOutput], output.value)
                chat_contents: List[ArrayChatMessageContentItem] = []
                for prompt_output in prompt_outputs:
                    if prompt_output.type == "STRING":
                        chat_contents.append(StringChatMessageContent(value=prompt_output.value))
                    elif prompt_output.type == "FUNCTION_CALL" and prompt_output.value:
                        raw_function_call = prompt_output.value.model_dump()
                        if "state" in raw_function_call:
                            del raw_function_call["state"]
                        chat_contents.append(
                            FunctionCallChatMessageContent(
                                value=FunctionCallChatMessageContentValue.model_validate(raw_function_call)
                            )
                        )

                if len(chat_contents) == 1:
                    if chat_contents[0].type == "STRING":
                        self.state.chat_history.append(ChatMessage(role="ASSISTANT", text=chat_contents[0].value))
                    else:
                        self.state.chat_history.append(ChatMessage(role="ASSISTANT", content=chat_contents[0]))
                else:
                    self.state.chat_history.append(
                        ChatMessage(role="ASSISTANT", content=ArrayChatMessageContent(value=chat_contents))
                    )

            yield output


class RouterNode(BaseNode[ToolCallingState]):
    """Router node that handles routing to function nodes based on outputs."""

    pass


class DynamicSubworkflowDeploymentNode(SubworkflowDeploymentNode[ToolCallingState], FunctionCallNodeMixin):
    """Node that executes a deployment definition with function call output."""

    def run(self) -> Iterator[BaseOutput]:
        arguments = self._extract_function_arguments()

        # Mypy doesn't like instance assignments of class attributes. It's safe in our case tho bc it's what
        # we do in the `__init__` method. Long term, instead of the function_call_output attribute above, we
        # want to do:
        # ```python
        # subworkflow_inputs = tool_prompt_node.Outputs.results[0]['value']['arguments'].if_(
        #     tool_prompt_node.Outputs.results[0]['type'].equals('FUNCTION_CALL'),
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
        # Extract arguments from function call
        arguments = self._extract_function_arguments()

        try:
            # Execute using ComposioService
            composio_service = ComposioService()
            if self.composio_tool.user_id is not None:
                result = composio_service.execute_tool(
                    tool_name=self.composio_tool.action, arguments=arguments, user_id=self.composio_tool.user_id
                )
            else:
                result = composio_service.execute_tool(tool_name=self.composio_tool.action, arguments=arguments)
        except Exception as e:
            raise NodeException(
                message=f"Error executing Composio tool '{self.composio_tool.action}': {str(e)}",
                code=WorkflowErrorCode.NODE_EXECUTION,
            )

        # Add result to chat history
        self._add_function_result_to_chat_history(result, self.state)

        yield from []


class MCPNode(BaseNode[ToolCallingState], FunctionCallNodeMixin):
    """Node that executes an MCP tool with function call output."""

    mcp_tool: MCPToolDefinition

    def run(self) -> Iterator[BaseOutput]:
        arguments = self._extract_function_arguments()

        try:
            mcp_service = MCPService()
            result = mcp_service.execute_tool(tool_def=self.mcp_tool, arguments=arguments)
        except Exception as e:
            raise NodeException(
                message=f"Error executing MCP tool '{self.mcp_tool.name}': {str(e)}",
                code=WorkflowErrorCode.NODE_EXECUTION,
            )

        # Add result to chat history
        self._add_function_result_to_chat_history(result, self.state)

        yield from []


class ElseNode(BaseNode[ToolCallingState]):
    """Node that executes when no function conditions match."""

    class Ports(BaseNode.Ports):
        # Redefined in the create_else_node function, but defined here to resolve mypy errors
        loop_to_router = Port.on_if(
            ToolCallingState.current_prompt_output_index.less_than(ToolPromptNode.Outputs.results.length())
        )
        loop_to_prompt = Port.on_elif(ToolCallingState.current_function_calls_processed.greater_than(0))
        end = Port.on_else()

    def run(self) -> BaseNode.Outputs:
        with self.state.__quiet__():
            self.state.current_prompt_output_index += 1
        return self.Outputs()


def _hydrate_composio_tool_definition(tool_def: ComposioToolDefinition) -> FunctionDefinition:
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

    except Exception as e:
        # If hydration fails (including no API key), log and return basic function definition
        logger.warning(f"Failed to enhance Composio tool '{tool_def.action}': {e}")
        return FunctionDefinition(
            name=tool_def.name,
            description=tool_def.description,
            parameters={},
        )


def hydrate_mcp_tool_definitions(server_def: MCPServer) -> List[MCPToolDefinition]:
    """Hydrate an MCPToolDefinition with detailed information from the MCP server.

    We do tool discovery on the MCP server to get the tool definitions.

    Args:
        tool_def: The basic MCPToolDefinition to enhance

    Returns:
        MCPToolDefinition with detailed parameters and description
    """
    try:
        mcp_service = MCPService()
        return mcp_service.hydrate_tool_definitions(server_def)
    except Exception as e:
        # If hydration fails, log and return original
        logger.warning(f"Failed to enhance MCP server '{server_def.name}': {e}")
        return []


def create_tool_prompt_node(
    ml_model: str,
    blocks: List[Union[PromptBlock, Dict[str, Any]]],
    functions: List[Tool],
    prompt_inputs: Optional[EntityInputsInterface],
    parameters: PromptParameters,
    max_prompt_iterations: Optional[int] = None,
) -> Type[ToolPromptNode]:
    if functions and len(functions) > 0:
        prompt_functions: List[Union[Tool, FunctionDefinition]] = []

        for function in functions:
            if isinstance(function, ComposioToolDefinition):
                # Get Composio tool details and hydrate the function definition
                enhanced_function = _hydrate_composio_tool_definition(function)
                prompt_functions.append(enhanced_function)
            elif isinstance(function, MCPServer):
                tool_functions: List[MCPToolDefinition] = hydrate_mcp_tool_definitions(function)
                for tool_function in tool_functions:
                    name = get_mcp_tool_name(tool_function)
                    prompt_functions.append(
                        FunctionDefinition(
                            name=name,
                            description=tool_function.description,
                            parameters=tool_function.parameters,
                        )
                    )
            else:
                prompt_functions.append(function)
    else:
        prompt_functions = []

    # Add a chat history block to blocks only if one doesn't already exist
    has_chat_history_block = any(
        (
            (block["block_type"] if isinstance(block, dict) else block.block_type) == "VARIABLE"
            and (
                block["input_variable"]
                if isinstance(block, dict)
                else block.input_variable if isinstance(block, VariablePromptBlock) else None
            )
            == CHAT_HISTORY_VARIABLE
        )
        for block in blocks
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
        Type[ToolPromptNode],
        type(
            "ToolPromptNode",
            (ToolPromptNode,),
            {
                "ml_model": ml_model,
                "blocks": blocks,
                "functions": prompt_functions,  # Use converted functions for prompt layer
                "prompt_inputs": node_prompt_inputs,
                "parameters": parameters,
                "max_prompt_iterations": max_prompt_iterations,
                "__module__": __name__,
            },
        ),
    )
    return node


def create_router_node(
    functions: List[Tool],
    tool_prompt_node: Type[InlinePromptNode[ToolCallingState]],
) -> Type[RouterNode]:
    """Create a RouterNode with dynamic ports that route based on tool_prompt_node outputs."""

    if functions and len(functions) > 0:
        # Create dynamic ports and convert functions in a single loop
        Ports = type("Ports", (), {})

        # Avoid using lambda to capture function_name
        # lambda will capture the function_name by reference,
        # and if the function_name is changed, the port_condition will also change.
        def create_port_condition(fn_name):
            return Port.on_if(
                ToolCallingState.current_prompt_output_index.less_than(tool_prompt_node.Outputs.results.length())
                & tool_prompt_node.Outputs.results[ToolCallingState.current_prompt_output_index]["type"].equals(
                    "FUNCTION_CALL"
                )
                & tool_prompt_node.Outputs.results[ToolCallingState.current_prompt_output_index]["value"][
                    "name"
                ].equals(fn_name)
            )

        for function in functions:
            if isinstance(function, ComposioToolDefinition):
                function_name = get_function_name(function)
                port = create_port_condition(function_name)
                setattr(Ports, function_name, port)
            elif isinstance(function, MCPServer):
                tool_functions: List[MCPToolDefinition] = hydrate_mcp_tool_definitions(function)
                for tool_function in tool_functions:
                    name = get_mcp_tool_name(tool_function)
                    port = create_port_condition(name)
                    setattr(Ports, name, port)
            else:
                function_name = get_function_name(function)
                port = create_port_condition(function_name)
                setattr(Ports, function_name, port)

        # Add the else port for when no function conditions match
        setattr(Ports, "default", Port.on_else())
    else:
        # If no functions exist, create a simple Ports class with just a default port
        Ports = type("Ports", (), {"default": Port(default=True)})

    node = cast(
        Type[RouterNode],
        type(
            "RouterNode",
            (RouterNode,),
            {
                "Ports": Ports,
                "prompt_outputs": tool_prompt_node.Outputs.results,
                "__module__": __name__,
            },
        ),
    )
    return node


def create_function_node(
    function: ToolBase,
    tool_prompt_node: Type[ToolPromptNode],
) -> Type[BaseNode]:
    """
    Create a FunctionNode class for a given function.

    For workflow functions: BaseNode
    For regular functions: BaseNode with direct function call

    Args:
        function: The function to create a node for
        tool_prompt_node: The tool prompt node class
    """
    if isinstance(function, DeploymentDefinition):
        deployment = function.deployment_id or function.deployment_name
        release_tag = function.release_tag

        node = type(
            f"DynamicSubworkflowDeploymentNode_{deployment}",
            (DynamicSubworkflowDeploymentNode,),
            {
                "deployment": deployment,
                "release_tag": release_tag,
                "function_call_output": tool_prompt_node.Outputs.results,
                "__module__": __name__,
            },
        )

        return node

    elif isinstance(function, ComposioToolDefinition):
        node = type(
            f"ComposioNode_{function.name}",
            (ComposioNode,),
            {
                "composio_tool": function,
                "function_call_output": tool_prompt_node.Outputs.results,
                "__module__": __name__,
            },
        )
        return node
    elif is_workflow_class(function):
        function.is_dynamic = True
        node = type(
            f"DynamicInlineSubworkflowNode_{function.__name__}",
            (DynamicInlineSubworkflowNode,),
            {
                "subworkflow": function,
                "function_call_output": tool_prompt_node.Outputs.results,
                "__module__": __name__,
            },
        )
    else:
        # For regular functions, use FunctionNode
        node = type(
            f"FunctionNode_{function.__name__}",
            (FunctionNode,),
            {
                "function_definition": lambda self, **kwargs: function(**kwargs),  # ← Revert back to lambda
                "function_call_output": tool_prompt_node.Outputs.results,
                "__module__": __name__,
            },
        )

    return node


def create_mcp_tool_node(
    tool_def: MCPToolDefinition,
    tool_prompt_node: Type[ToolPromptNode],
) -> Type[BaseNode]:
    node = type(
        f"MCPNode_{tool_def.name}",
        (MCPNode,),
        {
            "mcp_tool": tool_def,
            "function_call_output": tool_prompt_node.Outputs.results,
            "__module__": __name__,
        },
    )
    return node


def create_else_node(
    tool_prompt_node: Type[ToolPromptNode],
) -> Type[ElseNode]:
    class Ports(ElseNode.Ports):
        loop_to_router = Port.on_if(
            ToolCallingState.current_prompt_output_index.less_than(tool_prompt_node.Outputs.results.length())
        )
        loop_to_prompt = Port.on_elif(ToolCallingState.current_function_calls_processed.greater_than(0))
        end = Port.on_else()

    node = cast(
        Type[ElseNode],
        type(
            f"{tool_prompt_node.__name__}_ElseNode",
            (ElseNode,),
            {
                "Ports": Ports,
                "__module__": __name__,
            },
        ),
    )
    return node


def get_function_name(function: ToolBase) -> str:
    if isinstance(function, DeploymentDefinition):
        name = str(function.deployment_id or function.deployment_name)
        return name.replace("-", "")
    elif isinstance(function, ComposioToolDefinition):
        # model post init sets the name to the action if it's not set
        return function.name  # type: ignore[return-value]
    else:
        return snake_case(function.__name__)


def get_mcp_tool_name(tool_def: MCPToolDefinition) -> str:
    server_name = snake_case(tool_def.server.name)
    return f"{server_name}__{tool_def.name}"
