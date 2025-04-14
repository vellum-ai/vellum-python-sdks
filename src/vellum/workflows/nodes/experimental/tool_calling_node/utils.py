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

    def run(self) -> BaseNode.Outputs:
        # TODO: We should think about how to execute the function
        self.state.chat_history.append(
            ChatMessage(
                role="TOOL", text=f"Result from {self.function.name}: The current temperature is 22°C (71.6°F)."
            )
        )

        return self.Outputs()


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
    model_name: str,
    prompt_blocks: List[PromptBlock],
    functions: List[FunctionDefinition],
    input_values: Optional[EntityInputsInterface],
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
            "ml_model": model_name,
            "blocks": prompt_blocks,
            "functions": functions,
            "prompt_inputs": input_values,
            "Ports": Ports,
            "__module__": __name__,
        },
    )

    return node


def create_function_node(function: FunctionDefinition) -> Type[FunctionNode]:
    node = type(
        f"FunctionNode.{function.name}",
        (FunctionNode,),
        {
            "function": function,
            "__module__": __name__,
        },
    )

    return node
