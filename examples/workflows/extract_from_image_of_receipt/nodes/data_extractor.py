from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs


@TryNode.wrap()
class DataExtractor(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""\
You are an expert in extracting information from images of receipts. Your task is to accurately parse the receipt image and provide structured data based on the included schema. Only use the information from the image when creating the output and try to be as accurate as possible when grabbing the information from the image. If you don\'t know leave that portion of the JSON output empty
\
"""
                        )
                    ]
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "chat_history": Inputs.chat_history,
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=1000,
        top_p=1,
        top_k=0,
        frequency_penalty=0,
        presence_penalty=0,
        logit_bias={},
        custom_parameters={
            "json_schema": {
                "name": "schema",
                "schema": {
                    "type": "object",
                    "required": [
                        "provider_name",
                        "provider_address",
                        "provider_phone",
                        "date",
                        "items_in_receipt",
                        "number_of_items",
                        "payment_total",
                    ],
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date of purchase in the format mm/dd/yyyy.",
                        },
                        "payment_total": {
                            "type": "number",
                            "description": "Total amount of the receipt.",
                        },
                        "provider_name": {
                            "type": "string",
                            "description": "Name of the company that created the receipt.",
                        },
                        "provider_phone": {
                            "type": "string",
                            "description": "Phone number of the company that created the receipt.",
                        },
                        "number_of_items": {
                            "type": "number",
                            "description": "Total number of items on the receipt.",
                        },
                        "items_in_receipt": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "name",
                                    "price",
                                ],
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Name of the item.",
                                    },
                                    "price": {
                                        "type": "number",
                                        "description": "Price of the corresponding item.",
                                    },
                                },
                            },
                            "description": "List of items on the receipt.",
                        },
                        "provider_address": {
                            "type": "string",
                            "description": "Address of the company that created the receipt.",
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
    )
