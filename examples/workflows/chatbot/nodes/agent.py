from vellum import ChatMessagePromptBlock, PlainTextPromptBlock, RichTextPromptBlock, VariablePromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode

from ..inputs import Inputs
from ..state import State


class Agent(ToolCallingNode[State]):
    ml_model = "gpt-5-responses"
    prompt_inputs = {
        "user_message": Inputs.user_message,
        "chat_history": State.chat_history,
    }
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant. Use the prior conversation to stay consistent."
                        )
                    ]
                )
            ],
        ),
        # Insert prior turns before the new user turn
        VariablePromptBlock(input_variable="chat_history"),
        # Latest user message
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[RichTextPromptBlock(blocks=[VariablePromptBlock(input_variable="user_message")])],
        ),
    ]
    max_prompt_iterations = 25
