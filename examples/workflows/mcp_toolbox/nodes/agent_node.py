from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.types.definition import MCPServer

from ..inputs import Inputs


class Agent(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="""
You're a helpful hotel assistant. You handle hotel searching, booking and
cancellations. When the user searches for a hotel, mention it's name, id,
location and price tier. Always mention hotel ids while performing any
searches. This is very important for any operations. For any bookings or
cancellations, please provide the appropriate confirmation. Be sure to
update checkin or checkout dates if mentioned by the user.
Don't ask for confirmations from the user.
""",
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
            name="toolbox",
            url="http://127.0.0.1:5000/mcp",
        ),
    ]
    prompt_inputs = {
        "query": Inputs.query,
    }
