from collections.abc import Callable, Sequence
import inspect
import json
import types
from typing import Any, Iterator, List, Optional, Type, cast

from pydash import snake_case

from vellum import ChatMessage, PromptBlock
from vellum.client.types.code_execution_package import CodeExecutionPackage
from vellum.client.types.code_execution_runtime import CodeExecutionRuntime
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.code_execution_node.node import CodeExecutionNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.types.core import EntityInputsInterface, MergeBehavior
from vellum.workflows.types.generics import is_workflow_class


class FunctionNode(BaseNode):
    """Node that executes a specific function."""

    pass


class ToolRouterNode(InlinePromptNode):
    class Trigger(InlinePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ATTRIBUTES

    def run(self) -> Iterator[BaseOutput]:
        self.prompt_inputs = {**self.prompt_inputs, "chat_history": self.state.chat_history}  # type: ignore
        generator = super().run()
        for output in generator:
            if output.name == "results" and output.value:
                values = cast(List[Any], output.value)
                if values and len(values) > 0:
                    if values[0].type == "STRING":
                        self.state.chat_history.append(ChatMessage(role="ASSISTANT", text=values[0].value))
                    elif values[0].type == "FUNCTION_CALL":
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


def create_tool_router_node(
    ml_model: str,
    blocks: List[PromptBlock],
    functions: List[Callable[..., Any]],
    prompt_inputs: Optional[EntityInputsInterface],
) -> Type[ToolRouterNode]:
    if functions and len(functions) > 0:
        # If we have functions, create dynamic ports for each function
        Ports = type("Ports", (), {})
        for function in functions:
            function_name = snake_case(function.__name__)

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

    # Add a chat history block to blocks
    blocks.append(
        VariablePromptBlock(
            block_type="VARIABLE",
            input_variable="chat_history",
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
                "Ports": Ports,
                "__module__": __name__,
            },
        ),
    )
    return node


def create_function_node(
    function: Callable[..., Any],
    tool_router_node: Type[ToolRouterNode],
    packages: Optional[Sequence[CodeExecutionPackage]] = None,
    runtime: CodeExecutionRuntime = "PYTHON_3_11_6",
) -> Type[FunctionNode]:
    """
    Create a FunctionNode class for a given function.

    For workflow functions: BaseNode
    For regular functions: CodeExecutionNode with embedded function
    Args:
        function: The function to create a node for
        tool_router_node: The tool router node class
        packages: Optional list of packages to install for code execution (only used for regular functions)
        runtime: The runtime to use for code execution (default: "PYTHON_3_11_6")
    """
    if is_workflow_class(function):
        # Create a class-level wrapper that calls the original function
        def execute_function(self) -> BaseNode.Outputs:
            outputs = self.state.meta.node_outputs.get(tool_router_node.Outputs.text)

            outputs = json.loads(outputs)
            arguments = outputs["arguments"]

            # Call the function based on its type
            inputs_instance = function.get_inputs_class()(**arguments)

            workflow = function()
            terminal_event = workflow.run(
                inputs=inputs_instance,
            )
            if terminal_event.name == "workflow.execution.paused":
                raise NodeException(
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                    message="Subworkflow unexpectedly paused",
                )
            elif terminal_event.name == "workflow.execution.fulfilled":
                result = terminal_event.outputs
            elif terminal_event.name == "workflow.execution.rejected":
                raise Exception(f"Workflow execution rejected: {terminal_event.error}")

            self.state.chat_history.append(
                ChatMessage(
                    role="FUNCTION",
                    content=StringChatMessageContent(value=json.dumps(result, cls=DefaultStateEncoder)),
                )
            )

            return self.Outputs()

        # Create BaseNode for workflow functions
        node = type(
            f"InlineWorkflowNode_{function.__name__}",
            (FunctionNode,),
            {
                "run": execute_function,
                "__module__": __name__,
            },
        )
    else:
        # For regular functions, use CodeExecutionNode approach
        function_source = inspect.getsource(function)
        function_name = function.__name__

        code = f'''
{function_source}

def main(arguments):
    """Main function that calls the original function with the provided arguments."""
    return {function_name}(**arguments)
'''

        def execute_code_execution_function(self) -> BaseNode.Outputs:
            # Get the function call from the tool router output
            function_call_output = self.state.meta.node_outputs.get(tool_router_node.Outputs.results)
            if function_call_output and len(function_call_output) > 0:
                function_call = function_call_output[0]
                arguments = function_call.value.arguments
            else:
                arguments = {}

            self.code_inputs = {"arguments": arguments}

            outputs = base_class.run(self)

            self.state.chat_history.append(
                ChatMessage(
                    role="FUNCTION",
                    content=StringChatMessageContent(value=json.dumps(outputs.result, cls=DefaultStateEncoder)),
                )
            )

            return self.Outputs()

        # Create the properly typed base class with explicit type annotation
        def get_function_output_type() -> Type:
            return function.__annotations__.get("return", Any)

        output_type = get_function_output_type()

        base_class: Type[CodeExecutionNode] = CodeExecutionNode[BaseState, output_type]  # type: ignore[valid-type]

        # Create the class with basic attributes
        node = types.new_class(
            f"CodeExecutionNode_{function.__name__}",
            (base_class,),
            {},
            lambda ns: ns.update(
                {
                    "code": code,
                    "code_inputs": {},  # No inputs needed since we handle function call extraction in run()
                    "run": execute_code_execution_function,
                    "runtime": runtime,
                    "packages": packages,
                    "__module__": __name__,
                }
            ),
        )

    return node
