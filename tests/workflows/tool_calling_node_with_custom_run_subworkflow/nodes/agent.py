from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode

from .transform_text_tool import TransformTextToolWorkflow


class WorkflowInputs(BaseInputs):
    query: str


class AgentNode(ToolCallingNode):
    """
    A tool calling node that uses a subworkflow tool containing a custom node
    with a custom run method.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant that can transform text.",
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
                        VariablePromptBlock(
                            input_variable="question",
                        ),
                    ],
                ),
            ],
        ),
    ]
    functions = [TransformTextToolWorkflow]
    prompt_inputs = {
        "question": WorkflowInputs.query,
    }
