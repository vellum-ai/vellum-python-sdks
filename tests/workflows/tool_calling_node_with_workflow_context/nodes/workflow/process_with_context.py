from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.workflows.base import BaseWorkflow


def process_with_context(ctx: WorkflowContext, query: str) -> str:
    """
    Process a query with access to the workflow context.
    The WorkflowContext parameter should be excluded from the function schema
    and automatically injected at runtime.
    """
    return f"Processed: {query}"


class ContextAwareToolNode(ToolCallingNode):
    """
    A tool calling node with a function that has a WorkflowContext parameter.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant",
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
    functions = [process_with_context]
    prompt_inputs = {
        "question": "What can you help me with?",
    }


class ToolCallingNodeWithWorkflowContextWorkflow(BaseWorkflow):
    """
    A workflow that uses a tool calling node with a WorkflowContext parameter.
    """

    graph = ContextAwareToolNode

    class Outputs(BaseWorkflow.Outputs):
        text = ContextAwareToolNode.Outputs.text
        chat_history = ContextAwareToolNode.Outputs.chat_history
