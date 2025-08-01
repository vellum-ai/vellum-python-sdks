from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.workflows.nodes.displayable.tool_calling_node import ToolCallingNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import ComposioToolDefinition
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow


class Inputs(BaseInputs):
    query: str


github_create_issue_tool_with_user_id = ComposioToolDefinition(
    toolkit="GITHUB",
    action="GITHUB_CREATE_AN_ISSUE",
    description="Create a new issue in a GitHub repository",
    display_name="Create GitHub Issue",
    user_id="test_user_123",
)


class ComposioToolCallingNodeWithUserId(ToolCallingNode):
    """
    A tool calling node that uses a Composio tool with user_id to create GitHub issues.
    """

    ml_model = "gpt-4o-mini"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(
                            text=(
                                "You are a helpful assistant that can create GitHub issues. "
                                "When asked to create an issue, use the provided tool."
                            ),
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
    functions = [github_create_issue_tool_with_user_id]
    prompt_inputs = {
        "question": Inputs.query,
    }


class BasicToolCallingNodeWithComposioToolWithUserIdWorkflow(BaseWorkflow[Inputs, BaseState]):
    """
    A workflow that uses the ComposioToolCallingNodeWithUserId.
    """

    graph = ComposioToolCallingNodeWithUserId

    class Outputs(BaseWorkflow.Outputs):
        text = ComposioToolCallingNodeWithUserId.Outputs.text
        chat_history = ComposioToolCallingNodeWithUserId.Outputs.chat_history
