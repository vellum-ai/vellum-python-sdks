from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs


class PromptNode(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    prompt_inputs = {
        "query": Inputs.query,
        "context": Inputs.context,
    }
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                JinjaPromptBlock(
                    template=(
                        "Answer the following query: {{ inputs.query }}\n\n"
                        "Context: {{ inputs.context or 'No context provided' }}"
                    )
                )
            ],
        )
    ]
