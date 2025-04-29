from vellum import ChatMessagePromptBlock, FunctionDefinition, JinjaPromptBlock, PromptParameters, VariablePromptBlock
from vellum.workflows.nodes.displayable import InlinePromptNode

from ..inputs import Inputs
from .accumulate_chat_history import AccumulateChatHistory


class AgentNode(InlinePromptNode):
    """With the streaming API, we can send all intermediary messages / progress updates to the user while the Agent thinks and performs actions."""

    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""\
You are a helpful support bot that helps gather product information and answer questions for the user. Answer questions factually based  the information that you\'re provided and ask clarifying questions when needed.

Please provide your final answer in the following format:

Overall Recommendation: [Top recommendation]

Products Considered:
1. ...\
"""
                )
            ],
        ),
        VariablePromptBlock(input_variable="chat_history"),
    ]
    prompt_inputs = {
        "chat_history": AccumulateChatHistory.Outputs.result.coalesce(Inputs.chat_history),
    }
    functions = [
        FunctionDefinition(
            name="get_top_products",
            description="Gets the top rated home air products in the store",
            parameters={
                "type": "object",
                "properties": {},
            },
        ),
        FunctionDefinition(
            name="get_product_details",
            description="Gets price and customer review information for a specified product",
            parameters={
                "type": "object",
                "required": [
                    "product_name",
                ],
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name/identifier of the product",
                    },
                },
            },
        ),
    ]
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=1000,
        top_p=1,
        top_k=None,
        frequency_penalty=None,
        presence_penalty=None,
        logit_bias=None,
        custom_parameters=None,
    )
