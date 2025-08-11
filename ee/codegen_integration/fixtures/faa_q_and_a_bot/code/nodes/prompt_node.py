from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable import InlinePromptNode
from vellum.workflows.types.core import MergeBehavior

from .most_recent_message import MostRecentMessage


class PromptNode(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You are an expert classifier. You will analyze the chat and output one of the following in JSON format: 

1. \"weather\" if it is a question about the weather
2. \"flight status\" if it is about which flights are currently in transit at a certain airport
3. \"faa\" if the question is about any FAA related aviation policies
4. \"other\" if the question is about anything else\
"""
                        )
                    ]
                )
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER", blocks=[RichTextPromptBlock(blocks=[VariablePromptBlock(input_variable="var_1")])]
        ),
    ]
    prompt_inputs = {
        "var_1": MostRecentMessage.Outputs.result,
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=1000,
        top_p=1,
        top_k=None,
        frequency_penalty=0,
        presence_penalty=0,
        logit_bias={},
        custom_parameters={
            "json_mode": True,
            "json_schema": {
                "name": "Classification",
                "schema": {
                    "type": "object",
                    "required": [
                        "classification",
                    ],
                    "properties": {
                        "classification": {
                            "type": "string",
                            "description": "",
                        },
                    },
                },
            },
        },
    )

    class Trigger(InlinePromptNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY
