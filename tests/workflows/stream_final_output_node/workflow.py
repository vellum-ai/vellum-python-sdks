from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.jinja_prompt_block import JinjaPromptBlock
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.workflows.base import BaseWorkflow


class MyPrompt(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="Hello, world!",
                )
            ],
        )
    ]


class MyFinalOutput(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = MyPrompt.Outputs.text


class StreamFinalOutputWorkflow(BaseWorkflow):
    graph = MyPrompt >> MyFinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = MyFinalOutput.Outputs.value
