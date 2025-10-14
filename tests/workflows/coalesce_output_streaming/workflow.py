import random

from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.jinja_prompt_block import JinjaPromptBlock
from vellum.workflows.nodes import BaseNode
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.ports.port import Port
from vellum.workflows.references import LazyReference
from vellum.workflows.workflows.base import BaseWorkflow


class SwitchNode(BaseNode):
    class Ports(BaseNode.Ports):
        top = Port.on_if(LazyReference(lambda: SwitchNode.Outputs.condition.greater_than(0.5)))
        bottom = Port.on_else()

    class Outputs(BaseNode.Outputs):
        condition: int

    def run(self):
        condition = random.random()
        return self.Outputs(condition=condition)


class TopPromptNode(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="Hello",
                )
            ],
        )
    ]


class BottomPromptNode(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="World",
                )
            ],
        )
    ]


class FinalOutput(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        score = TopPromptNode.Outputs.text.coalesce(BottomPromptNode.Outputs.text)


class CoalesceOutputStreamingTestWorkflow(BaseWorkflow):
    graph = {
        SwitchNode.Ports.top >> TopPromptNode,
        SwitchNode.Ports.bottom >> BottomPromptNode,
    } >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_score = FinalOutput.Outputs.score
