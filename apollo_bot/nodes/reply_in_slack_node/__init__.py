from typing import List

from vellum import ChatMessage, ChatMessagePromptBlock, JinjaPromptBlock, PromptParameters
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.triggers import SlackTrigger
from vellum.workflows.types.definition import VellumIntegrationToolDefinition

from ..create_linear_ticket_node import CreateLinearTicketNode


class ReplyInSlackNode(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""\
Reply to the Slack message in channel {{ channel_id }} at thread {{ message_ts }}.

Use the SLACK_SEND_MESSAGE tool with:
- channel: {{ channel_id }}
- thread_ts: {{ message_ts }}
- markdown_text: \"Linear ticket created: {{ ticket_url }}\"

Confirm when the message has been sent.\
"""
                )
            ],
        ),
    ]
    prompt_inputs = {
        "channel_id": SlackTrigger.Outputs.channel,
        "message_ts": SlackTrigger.Outputs.timestamp,
        "ticket_url": CreateLinearTicketNode.Outputs.text,
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=500,
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
            name="SLACK_SEND_MESSAGE",
            description="Sends a message to a Slack channel",
        )
    ]
    max_prompt_iterations = 3
    settings = None

    class Outputs(ToolCallingNode.Outputs):
        text: str
        chat_history: List[ChatMessage]
