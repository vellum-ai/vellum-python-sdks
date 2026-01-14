from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.jinja_prompt_block import JinjaPromptBlock
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    pass


class Chat(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="Write a haiku about the ocean",
                )
            ],
        )
    ]


class HaikuHelper(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="Improve this haiku: {{ haiku }}",
                )
            ],
        )
    ]
    prompt_inputs = {
        "haiku": Chat.Outputs.text,
    }


class ChatPromptOutputStreamingWorkflow(BaseWorkflow[Inputs, BaseState]):
    """
    This workflow tests that Chat Prompt Output Streaming works at the workflow level
    when there are multiple prompt nodes in sequence.

    The expected behavior is that streaming events from HaikuHelper should be emitted
    at the workflow level since the workflow output references HaikuHelper.Outputs.text.
    """

    graph = Chat >> HaikuHelper

    class Outputs(BaseWorkflow.Outputs):
        response = HaikuHelper.Outputs.text
