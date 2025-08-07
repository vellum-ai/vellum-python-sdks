from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.constants import AuthorizationType
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.types.definition import MCPServer

from ..inputs import Inputs


class MyPromptNode(ToolCallingNode):
    """
    A tool calling node that uses the GitHub MCP server to manage the user's GitHub account.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant that will manage the user's Github account on their behalf.",
                        ),
                    ],
                ),
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                VariablePromptBlock(
                    input_variable="query",
                ),
            ],
        ),
    ]
    functions = [
        MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            authorization_type=AuthorizationType.BEARER_TOKEN,
            bearer_token_value=EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN"),
        ),
    ]
    prompt_inputs = {
        "query": Inputs.query,
    }
