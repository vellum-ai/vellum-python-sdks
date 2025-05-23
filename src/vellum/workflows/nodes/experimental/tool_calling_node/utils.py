from collections.abc import Callable
import json
from typing import Any, Iterator, List, Optional, Type, cast

from pydash import snake_case

from vellum import ChatMessage, PromptBlock
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
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


def create_function_node(function: Callable[..., Any], tool_router_node: Type[ToolRouterNode]) -> Type[FunctionNode]:
    """
    Create a FunctionNode class for a given function.

    This ensures the callable is properly registered and can be called with the expected arguments.
    """

    # Create a class-level wrapper that calls the original function
    def execute_function(self) -> BaseNode.Outputs:
        outputs = self.state.meta.node_outputs.get(tool_router_node.Outputs.text)
        # first parse into json
        outputs = json.loads(outputs)
        arguments = outputs["arguments"]

        # Call the function based on its type
        if is_workflow_class(function):
            # Dynamically define an Inputs subclass of BaseInputs
            Inputs = type(
                "Inputs",
                (BaseInputs,),
                {"__annotations__": {k: type(v) for k, v in arguments.items()}},
            )

            # Create an instance with arguments
            inputs_instance = Inputs(**arguments)

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
        else:
            # If it's a regular callable, call it directly
            result = function(**arguments)

        self.state.chat_history.append(
            ChatMessage(
                role="FUNCTION",
                content=StringChatMessageContent(value=json.dumps(result, cls=DefaultStateEncoder)),
            )
        )

        return self.Outputs()

    node = type(
        f"FunctionNode_{function.__name__}",
        (FunctionNode,),
        {
            "run": execute_function,
            "__module__": __name__,
        },
    )

    return node
