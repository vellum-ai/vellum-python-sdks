from typing import Iterator

from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.jinja_prompt_block import JinjaPromptBlock
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.outputs import BaseOutput
from vellum.workflows.workflows.base import BaseWorkflow


class BaseTextNode(BaseNode):
    """
    A simple base node that outputs text.
    """

    class Outputs(BaseNode.Outputs):
        text: str

    def run(self) -> Iterator[BaseOutput]:
        text = "Hello from base node"
        yield BaseOutput(name="text", value=text)


class MyInlinePromptNode(InlinePromptNode):
    """
    An inline prompt node that references the base node's text output.
    """

    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="{{ base_text }}",
                )
            ],
        )
    ]
    prompt_inputs = {
        "base_text": BaseTextNode.Outputs.text,
    }


class MyFinalOutputNode(FinalOutputNode):
    """
    A final output node that references the inline prompt node's text output.
    """

    class Outputs(FinalOutputNode.Outputs):
        value = MyInlinePromptNode.Outputs.text


class BasicStreamingInlinePromptWorkflow(BaseWorkflow):
    """
    A workflow that streams text deltas from an inline prompt node.
    """

    graph = BaseTextNode >> MyInlinePromptNode >> MyFinalOutputNode

    class Outputs(BaseWorkflow.Outputs):
        final_output = MyFinalOutputNode.Outputs.value
        prompt_text = MyInlinePromptNode.Outputs.text
