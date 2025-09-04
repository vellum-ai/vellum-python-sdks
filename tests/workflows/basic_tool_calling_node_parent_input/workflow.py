from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow

from tests.workflows.basic_tool_calling_node_parent_input.nodes.dummy_node import DummyNode

from .get_string import get_string
from .inputs import ParentInputs


class StringToolCallingNode(ToolCallingNode):
    """
    A tool calling node that receives inputs from parent workflow and user-defined inputs.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a string expert. Use the provided parent input.",
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
    functions = [get_string]
    prompt_inputs = {
        "question": "What's the string like?",
    }


class BasicToolCallingNodeParentInputWorkflow(BaseWorkflow[ParentInputs, BaseState]):
    """
    A parent workflow that passes inputs to a tool calling node.
    """

    graph = DummyNode >> StringToolCallingNode

    class Outputs(BaseWorkflow.Outputs):
        text = StringToolCallingNode.Outputs.text
        chat_history = StringToolCallingNode.Outputs.chat_history
