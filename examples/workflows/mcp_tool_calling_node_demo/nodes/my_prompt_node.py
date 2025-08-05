from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, RichTextPromptBlock, VariablePromptBlock
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.ports import Port
from vellum.workflows.references import LazyReference

from ..inputs import Inputs
from ..state import State
from .mcp_client_node import MCPClientNode


class MyPromptNode(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant that will manage the user's Github account on their behalf.",
                        )
                    ]
                )
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                VariablePromptBlock(
                    input_variable="query",
                ),
            ],
        ),
        VariablePromptBlock(
            input_variable="chat_history",
        ),
    ]
    prompt_inputs = {
        "query": Inputs.query,
        "chat_history": State.chat_history.coalesce([]),
    }
    # Our mypy plugin is not handling list of pydantic models properly
    functions = MCPClientNode.Outputs.tools  # type: ignore[assignment]

    class Ports(InlinePromptNode.Ports):
        action = Port.on_if(LazyReference(lambda: MyPromptNode.Outputs.results[0]["type"].equals("FUNCTION_CALL")))
        exit = Port.on_if(LazyReference(lambda: MyPromptNode.Outputs.results[0]["type"].equals("STRING")))

    class Outputs(InlinePromptNode.Outputs):
        thinking = "Asking the model..."
