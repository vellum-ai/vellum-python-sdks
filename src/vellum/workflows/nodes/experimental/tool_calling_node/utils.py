from collections.abc import Callable
import json
from typing import Iterator, List, Optional, Type

from vellum import ChatMessage, FunctionDefinition, PromptBlock
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.outputs.base import BaseOutput
from vellum.workflows.ports.port import Port
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.types.core import EntityInputsInterface


class FunctionNode(BaseNode):
    """Node that executes a specific function."""

    function: FunctionDefinition


class ToolRouterNode(InlinePromptNode):
    # TODO: We should include chat history in our next prompt input
    def run(self) -> Iterator[BaseOutput]:
        generator = super().run()
        text = None
        for output in generator:
            if output.name == "text":
                text = output.value
                if hasattr(self.state, "chat_history"):
                    self.state.chat_history.append(ChatMessage(role="ASSISTANT", text=text))
            yield output


def create_tool_router_node(
    ml_model: str,
    blocks: List[PromptBlock],
    functions: List[FunctionDefinition],
    prompt_inputs: Optional[EntityInputsInterface],
) -> Type[ToolRouterNode]:
    Ports = type("Ports", (), {})
    for function in functions:
        # TODO: We should think about how to handle this
        if function.name is None:
            raise ValueError("Function name is required")
        function_name = function.name
        port_condition = LazyReference(
            lambda: (
                ToolRouterNode.Outputs.results[0]["type"].equals("FUNCTION_CALL")
                & ToolRouterNode.Outputs.results[0]["value"]["name"].equals(function_name)
            )
        )
        port = Port.on_if(port_condition)
        setattr(Ports, function_name, port)

    setattr(Ports, "default", Port.on_else())
    node = type(
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
    )

    return node


def create_function_node(function: FunctionDefinition, function_callable: Callable) -> Type[FunctionNode]:
    """
    Create a FunctionNode class for a given function.

    This ensures the callable is properly registered and can be called with the expected arguments.
    """

    # Create a class-level wrapper that calls the original function
    def execute_function(self) -> BaseNode.Outputs:
        outputs = self.state.meta.node_outputs.get(ToolRouterNode.Outputs.text)
        # first parse into json
        outputs = json.loads(outputs)
        arguments = outputs["arguments"]

        # Call the original function directly with the arguments
        result = function_callable(**arguments)

        self.state.chat_history.append(ChatMessage(role="FUNCTION", text=result))

        return self.Outputs()

    node = type(
        f"FunctionNode_{function.name}",
        (FunctionNode,),
        {
            "function": function,
            "run": execute_function,
            "__module__": __name__,
        },
    )

    return node
