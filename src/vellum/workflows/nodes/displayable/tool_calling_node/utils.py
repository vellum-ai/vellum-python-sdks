import json
from typing import Any, Callable, Iterator, List, Optional, Type, cast

from pydash import snake_case

from vellum import ChatMessage, PromptBlock
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_parameters import PromptParameters
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.inline_subworkflow_node.node import InlineSubworkflowNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.displayable.subworkflow_deployment_node.node import SubworkflowDeploymentNode
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state import BaseState
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.core import EntityInputsInterface, MergeBehavior, Tool
from vellum.workflows.types.definition import DeploymentDefinition
from vellum.workflows.types.generics import is_workflow_class

CHAT_HISTORY_VARIABLE = "chat_history"


class ToolRouterNode(InlinePromptNode[ToolCallingState]):
    max_prompt_iterations: Optional[int] = 5

    class Trigger(InlinePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES

    def run(self) -> Iterator[BaseOutput]:
        if self.state.prompt_iterations >= self.max_prompt_iterations:
            max_iterations_message = f"Maximum number of prompt iterations `{self.max_prompt_iterations}` reached."
            raise NodeException(message=max_iterations_message, code=WorkflowErrorCode.NODE_EXECUTION)

        # Merge user-provided chat history with node's chat history
        user_chat_history = self.prompt_inputs.get(CHAT_HISTORY_VARIABLE, []) if self.prompt_inputs else []
        merged_chat_history = user_chat_history + self.state.chat_history
        self.prompt_inputs = {**self.prompt_inputs, CHAT_HISTORY_VARIABLE: merged_chat_history}  # type: ignore
        generator = super().run()
        for output in generator:
            if output.name == "results" and output.value:
                values = cast(List[Any], output.value)
                if values and len(values) > 0:
                    if values[0].type == "STRING":
                        self.state.chat_history.append(ChatMessage(role="ASSISTANT", text=values[0].value))
                    elif values[0].type == "FUNCTION_CALL":
                        self.state.prompt_iterations += 1

                        function_call = values[0].value
                        if function_call is not None:
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
            yield output


class DynamicSubworkflowDeploymentNode(SubworkflowDeploymentNode[ToolCallingState]):
    """Node that executes a deployment definition with function call output."""

    function_call_output: List[PromptOutput]

    def run(self) -> Iterator[BaseOutput]:
        if self.function_call_output and len(self.function_call_output) > 0:
            function_call = self.function_call_output[0]
            if function_call.type == "FUNCTION_CALL" and function_call.value is not None:
                arguments = function_call.value.arguments
            else:
                arguments = {}
        else:
            arguments = {}

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
        self.state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=json.dumps(outputs, cls=DefaultStateEncoder)),
            )
        )


class DynamicInlineSubworkflowNode(InlineSubworkflowNode[ToolCallingState, BaseInputs, BaseState]):
    """Node that executes an inline subworkflow with function call output."""

    function_call_output: List[PromptOutput]

    def run(self) -> Iterator[BaseOutput]:
        if self.function_call_output and len(self.function_call_output) > 0:
            function_call = self.function_call_output[0]
            if function_call.type == "FUNCTION_CALL" and function_call.value is not None:
                arguments = function_call.value.arguments
            else:
                arguments = {}
        else:
            arguments = {}

        self.subworkflow_inputs = arguments  # type: ignore[misc]

        # Call the parent run method to execute the subworkflow with proper streaming
        outputs = {}

        for output in super().run():
            if output.is_fulfilled:
                outputs[output.name] = output.value
            yield output

        # Add the result to the chat history
        self.state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=json.dumps(outputs, cls=DefaultStateEncoder)),
            )
        )


class FunctionNode(BaseNode[ToolCallingState]):
    """Node that executes a regular Python function with function call output."""

    function_call_output: List[PromptOutput]
    function_definition: Callable[..., Any]

    def run(self) -> Iterator[BaseOutput]:
        if self.function_call_output and len(self.function_call_output) > 0:
            function_call = self.function_call_output[0]
            if function_call.type == "FUNCTION_CALL" and function_call.value is not None:
                arguments = function_call.value.arguments
            else:
                arguments = {}
        else:
            arguments = {}

        try:
            result = self.function_definition(**arguments)
        except Exception as e:
            function_name = self.function_definition.__name__
            raise NodeException(
                message=f"Error executing function '{function_name}': {str(e)}",
                code=WorkflowErrorCode.NODE_EXECUTION,
            )

        # Add the result to the chat history
        self.state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=json.dumps(result, cls=DefaultStateEncoder)),
            )
        )

        yield from []


def create_tool_router_node(
    ml_model: str,
    blocks: List[PromptBlock],
    functions: List[Tool],
    prompt_inputs: Optional[EntityInputsInterface],
    parameters: PromptParameters,
    max_prompt_iterations: Optional[int] = None,
) -> Type[ToolRouterNode]:
    if functions and len(functions) > 0:
        # If we have functions, create dynamic ports for each function
        Ports = type("Ports", (), {})
        for function in functions:
            function_name = get_function_name(function)

            # Avoid using lambda to capture function_name
            # lambda will capture the function_name by reference,
            # and if the function_name is changed, the port_condition will also change.
            def create_port_condition(fn_name):
                return LazyReference(
                    lambda: (
                        node.Outputs.results[0]["type"].equals("FUNCTION_CALL")
                        & node.Outputs.results[0]["value"]["name"].equals(fn_name)
                    )
                )

            port_condition = create_port_condition(function_name)
            port = Port.on_if(port_condition)
            setattr(Ports, function_name, port)

        # Add the else port for when no function conditions match
        setattr(Ports, "default", Port.on_else())
    else:
        # If no functions exist, create a simple Ports class with just a default port
        Ports = type("Ports", (), {"default": Port(default=True)})

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

    node = cast(
        Type[ToolRouterNode],
        type(
            "ToolRouterNode",
            (ToolRouterNode,),
            {
                "ml_model": ml_model,
                "blocks": blocks,
                "functions": functions,
                "prompt_inputs": prompt_inputs,
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

    Args:
        function: The function to create a node for
        tool_router_node: The tool router node class
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
                "function_call_output": tool_router_node.Outputs.results,
                "__module__": __name__,
            },
        )

        return node

    elif is_workflow_class(function):
        node = type(
            f"DynamicInlineSubworkflowNode_{function.__name__}",
            (DynamicInlineSubworkflowNode,),
            {
                "subworkflow": function,
                "function_call_output": tool_router_node.Outputs.results,
                "__module__": __name__,
            },
        )
    else:
        # For regular functions, use FunctionNode
        node = type(
            f"FunctionNode_{function.__name__}",
            (FunctionNode,),
            {
                "function_definition": lambda self, **kwargs: function(**kwargs),
                "function_call_output": tool_router_node.Outputs.results,
                "__module__": __name__,
            },
        )

    return node


def get_function_name(function: Tool) -> str:
    if isinstance(function, DeploymentDefinition):
        name = str(function.deployment_id or function.deployment_name)
        return name.replace("-", "")
    else:
        return snake_case(function.__name__)
