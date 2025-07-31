from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.constants import AuthorizationType
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import MCPServer
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow


class Inputs(BaseInputs):
    query: str


class CreateRepositoryNode(ToolCallingNode):
    """
    A tool calling node that calls the create_repository function.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text="You are a helpful assistant",
                        ),
                    ],
                ),
            ],
        ),
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        VariablePromptBlock(
                            input_variable="question",
                        ),
                    ],
                ),
            ],
        ),
    ]
    functions = []
    tool_sources = [
        MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            authorization_type=AuthorizationType.BEARER_TOKEN,
            bearer_token_value=EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN"),
        ),
    ]
    prompt_inputs = {
        "question": Inputs.query,
    }


class BasicToolCallingNodeMCPWorkflow(BaseWorkflow[Inputs, BaseState]):
    """
    A workflow that uses the CreateRepositoryNode.
    """

    graph = CreateRepositoryNode

    class Outputs(BaseWorkflow.Outputs):
        text = CreateRepositoryNode.Outputs.text
        chat_history = CreateRepositoryNode.Outputs.chat_history
