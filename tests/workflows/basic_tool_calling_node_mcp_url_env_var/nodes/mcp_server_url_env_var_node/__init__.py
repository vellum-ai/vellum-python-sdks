from vellum import (
    ChatMessagePromptBlock,
    PlainTextPromptBlock,
    PromptParameters,
    RichTextPromptBlock,
    VariablePromptBlock,
)
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.references import EnvironmentVariableReference
from vellum.workflows.types.definition import MCPServer

from ...inputs import Inputs


class MCPServerUrlEnvVarNode(ToolCallingNode):
    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text="""You are a helpful assistant""")])],
        ),
        ChatMessagePromptBlock(
            chat_role="USER", blocks=[RichTextPromptBlock(blocks=[VariablePromptBlock(input_variable="question")])]
        ),
    ]
    functions = [
        MCPServer(
            type="MCP_SERVER",
            name="my-mcp-server",
            description="",
            url=EnvironmentVariableReference(name="MCP_SERVER_URL"),
        )
    ]
    prompt_inputs = {
        "question": Inputs.query,
    }
    parameters = PromptParameters(
        stop=[],
        temperature=0,
        max_tokens=4096,
        top_p=1,
        top_k=0,
        frequency_penalty=0,
        presence_penalty=0,
        logit_bias=None,
        custom_parameters=None,
    )
    max_prompt_iterations = 25
    settings = None
