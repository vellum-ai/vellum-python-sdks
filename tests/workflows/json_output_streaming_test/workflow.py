from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.jinja_prompt_block import JinjaPromptBlock
from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.workflows.base import BaseWorkflow


class PromptNode(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template="Please provide a score and reasoning in JSON format.",
                )
            ],
        )
    ]


class FinalOutput(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        score = PromptNode.Outputs.json["score"]


class JsonOutputStreamingTestWorkflow(BaseWorkflow):
    graph = PromptNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_score = FinalOutput.Outputs.score
