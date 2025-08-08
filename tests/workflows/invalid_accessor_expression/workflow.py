from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.inline_prompt_node import InlinePromptNode


class FirstNode(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""You are a helpful assistant that can answer questions and help with tasks."""
                        )
                    ]
                )
            ],
        ),
    ]
    prompt_inputs = {}


class InvalidAccessorExpressionNode(BaseNode):
    value = FirstNode.Outputs.results[0]["no_value"]  # type: ignore

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:  # type: ignore[empty-body]
        pass


class InvalidAccessorExpressionWorkflow(BaseWorkflow):
    graph = FirstNode >> InvalidAccessorExpressionNode

    class Outputs(BaseWorkflow.Outputs):
        result = InvalidAccessorExpressionNode.Outputs.result
