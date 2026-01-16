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


class MultipleAliasedPromptOutputsWorkflow(BaseWorkflow[Inputs, BaseState]):
    """
    This workflow tests that streaming events are emitted for ALL workflow outputs
    that alias the same prompt node's text output.

    The expected behavior is that streaming events from Chat should be emitted
    at the workflow level for BOTH response and response_copy outputs.
    """

    graph = Chat

    class Outputs(BaseWorkflow.Outputs):
        response = Chat.Outputs.text
        response_copy = Chat.Outputs.text
