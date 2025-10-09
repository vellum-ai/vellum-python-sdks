from typing import List

from vellum import ChatMessage, ChatMessagePromptBlock, JinjaPromptBlock, PromptParameters
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.types.definition import VellumIntegrationToolDefinition

from ..check_tag_node import CheckTagNode


class CreateLinearTicketNode(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    template="""\
Create a Linear issue for the following message:

{{ message_text }}

Use the LINEAR_CREATE_LINEAR_ISSUE tool with:
- title: Create a concise title summarizing the issue
- description: Use the message text as the description
- team_id: You\'ll need to determine the appropriate team ID

After creating the ticket, return the ticket URL.\
"""
                )
            ],
        ),
    ]
    prompt_inputs = {
        "message_text": CheckTagNode.Outputs.message_text,
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
            integration_name="linear",
            name="LINEAR_CREATE_LINEAR_ISSUE",
            description="Creates a new issue in Linear",
        ),
        VellumIntegrationToolDefinition(
            provider="COMPOSIO",
            integration_name="linear",
            name="LINEAR_GET_ALL_LINEAR_TEAMS",
            description="Gets all Linear teams to find the appropriate team ID",
        ),
    ]
    max_prompt_iterations = 5
    settings = None

    class Outputs(ToolCallingNode.Outputs):
        text: str
        chat_history: List[ChatMessage]
