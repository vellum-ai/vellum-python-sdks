from typing import List

from vellum import ChatMessage, ChatMessagePromptBlock, JinjaPromptBlock, PromptParameters
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.types.definition import VellumIntegrationToolDefinition

from ..parse_slack_url_node import ParseSlackUrlNode


class FetchSlackMessageNode(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""\
Fetch the Slack message from channel {{ channel_id }} with timestamp {{ message_ts }}.
Use the SLACK_FETCH_CONVERSATION_HISTORY tool with:
- channel: {{ channel_id }}
- oldest: {{ message_ts }}
- latest: {{ message_ts }}
- limit: 1

Return the message text from the response.\
"""
                )
            ],
        ),
    ]
    prompt_inputs = {
        "channel_id": ParseSlackUrlNode.Outputs.channel_id,
        "message_ts": ParseSlackUrlNode.Outputs.message_ts,
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=1000,
        top_p=None,
        top_k=None,
        frequency_penalty=None,
        presence_penalty=None,
        logit_bias=None,
        custom_parameters=None,
    )
    functions = [
        VellumIntegrationToolDefinition(
            provider="COMPOSIO",
            integration_name="slack",
            name="SLACK_FETCH_CONVERSATION_HISTORY",
            description="Fetches conversation history from a Slack channel",
        )
    ]
    max_prompt_iterations = 3
    settings = None

    class Outputs(ToolCallingNode.Outputs):
        text: str
        chat_history: List[ChatMessage]
