from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode

from .process_with_context import process_with_context


class ContextAwareToolNode(ToolCallingNode):
    """
    A tool calling node with a function that has a WorkflowContext parameter.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text="""You are a helpful assistant""")])],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(blocks=[VariablePromptBlock(input_variable="98df5f55-1a82-45bc-9c4d-d11b33154021")])
            ],
        ),
    ]
    functions = [process_with_context]
    prompt_inputs = {
        "question": "What can you help me with?",
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=4096,
        top_p=1,
        top_k=0,
        frequency_penalty=0,
        presence_penalty=0,
        logit_bias=None,
        custom_parameters=None,
    )
    max_prompt_iterations = 25
    settings = None
