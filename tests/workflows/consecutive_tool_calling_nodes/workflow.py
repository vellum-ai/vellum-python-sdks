from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.workflows.base import BaseWorkflow


class FirstToolCallingNode(ToolCallingNode):
    """
    First tool calling node with no tools defined.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant. This is the first node.",
                        ),
                    ],
                ),
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="Please respond with 'First node response'",
                        ),
                    ],
                ),
            ],
        ),
    ]
    functions = []
    prompt_inputs = {}


class SecondToolCallingNode(ToolCallingNode):
    """
    Second tool calling node with no tools defined.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant. This is the second node.",
                        ),
                    ],
                ),
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="Please respond with 'Second node response'",
                        ),
                    ],
                ),
            ],
        ),
    ]
    functions = []
    prompt_inputs = {}


class ConsecutiveToolCallingNodesWorkflow(BaseWorkflow):
    """
    A workflow that uses two consecutive ToolCallingNodes with no tools defined.
    This should demonstrate the bug where the second node doesn't execute.
    """

    graph = FirstToolCallingNode >> SecondToolCallingNode

    class Outputs(BaseWorkflow.Outputs):
        text = SecondToolCallingNode.Outputs.text
        chat_history = SecondToolCallingNode.Outputs.chat_history
