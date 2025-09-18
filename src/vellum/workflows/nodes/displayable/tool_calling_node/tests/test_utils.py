import pytest
from uuid import uuid4

from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.prompt_settings import PromptSettings
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.tool_calling_node.utils import (
    create_tool_prompt_node,
    get_function_name,
    get_mcp_tool_name,
)
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.definition import ComposioToolDefinition, DeploymentDefinition, MCPServer, MCPToolDefinition


def test_get_function_name_callable():
    """Test callable"""

    def my_function() -> str:
        return "test"

    function = my_function

    result = get_function_name(function)

    assert result == "my_function"


def test_get_function_name_workflow_class():
    """Test workflow class."""

    class MyWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        class MyNode(BaseNode):
            class Outputs(BaseOutputs):
                result: str

            def run(self) -> Outputs:
                return self.Outputs(result="test")

        graph = MyNode

    workflow_class = MyWorkflow

    result = get_function_name(workflow_class)

    assert result == "my_workflow"


def test_get_function_name_subworkflow_deployment():
    """Test subworkflow deployment."""
    deployment_config = DeploymentDefinition(deployment="my-test-deployment", release_tag="v1.0.0")

    result = get_function_name(deployment_config)

    assert result == "mytestdeployment"


def test_get_function_name_subworkflow_deployment_uuid():
    """Test subworkflow deployment with UUID."""
    deployment_config = DeploymentDefinition(deployment="57f09beb-b463-40e0-bf9e-c972e664352f", release_tag="v1.0.0")

    result = get_function_name(deployment_config)

    assert result == "57f09bebb46340e0bf9ec972e664352f"


def test_get_function_name_mcp_tool_definition():
    """Test MCPToolDefinition function name generation."""
    mcp_tool = MCPToolDefinition(
        name="create_repository",
        server=MCPServer(name="github", url="https://api.github.com"),
        parameters={"repository_name": "string", "description": "string"},
    )

    result = get_mcp_tool_name(mcp_tool)

    assert result == "github__create_repository"


@pytest.mark.parametrize(
    "toolkit,action,description,expected_result",
    [
        ("SLACK", "SLACK_SEND_MESSAGE", "Send message to Slack", "slack_send_message"),
        ("GMAIL", "GMAIL_CREATE_EMAIL_DRAFT", "Create Gmail draft", "gmail_create_email_draft"),
    ],
)
def test_get_function_name_composio_tool_definition_various_toolkits(
    toolkit: str, action: str, description: str, expected_result: str
):
    """Test ComposioToolDefinition function name generation with various toolkits."""
    composio_tool = ComposioToolDefinition(toolkit=toolkit, action=action, description=description, user_id=None)

    result = get_function_name(composio_tool)

    assert result == expected_result


def test_create_tool_prompt_node_max_prompt_iterations(vellum_adhoc_prompt_client):
    # GIVEN a tool router node with max_prompt_iterations set to None
    tool_prompt_node = create_tool_prompt_node(
        ml_model="gpt-4o-mini",
        blocks=[],
        functions=[],
        prompt_inputs=None,
        parameters=DEFAULT_PROMPT_PARAMETERS,
        max_prompt_iterations=None,
    )

    def generate_prompt_events(*args, **kwargs):
        execution_id = str(uuid4())
        events = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=[StringVellumValue(value="test output")],
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the tool router node
    node_instance = tool_prompt_node()
    outputs = list(node_instance.run())
    assert outputs[0].name == "results"
    assert outputs[0].value == [StringVellumValue(type="STRING", value="test output")]
    assert outputs[1].name == "text"
    assert outputs[1].value == "test output"


def test_create_tool_prompt_node_chat_history_block_dict(vellum_adhoc_prompt_client):
    # GIVEN a list of blocks with a chat history block
    blocks = [
        {
            "block_type": "CHAT_MESSAGE",
            "chat_role": "SYSTEM",
            "blocks": [
                {
                    "block_type": "RICH_TEXT",
                    "blocks": [{"block_type": "PLAIN_TEXT", "cache_config": None, "text": "first message"}],
                }
            ],
        },
        {
            "block_type": "CHAT_MESSAGE",
            "chat_role": "USER",
            "blocks": [
                {
                    "block_type": "RICH_TEXT",
                    "blocks": [
                        {"block_type": "PLAIN_TEXT", "text": "second message"},
                        {"block_type": "PLAIN_TEXT", "text": "third message"},
                    ],
                }
            ],
        },
    ]

    tool_prompt_node = create_tool_prompt_node(
        ml_model="gpt-4o-mini",
        blocks=blocks,  # type: ignore
        functions=[],
        prompt_inputs=None,
        parameters=DEFAULT_PROMPT_PARAMETERS,
    )

    def generate_prompt_events(*args, **kwargs):
        execution_id = str(uuid4())
        events = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=[StringVellumValue(value="test output")],
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN we run the tool router node
    node_instance = tool_prompt_node()
    list(node_instance.run())

    # THEN the API was called with compiled blocks
    blocks = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args[1]["blocks"]
    assert blocks == [
        ChatMessagePromptBlock(
            block_type="CHAT_MESSAGE",
            state=None,
            cache_config=None,
            chat_role="SYSTEM",
            chat_source=None,
            chat_message_unterminated=None,
            blocks=[
                RichTextPromptBlock(
                    block_type="RICH_TEXT",
                    state=None,
                    cache_config=None,
                    blocks=[
                        PlainTextPromptBlock(
                            block_type="PLAIN_TEXT", state=None, cache_config=None, text="first message"
                        )
                    ],
                )
            ],
        ),
        ChatMessagePromptBlock(
            block_type="CHAT_MESSAGE",
            state=None,
            cache_config=None,
            chat_role="USER",
            chat_source=None,
            chat_message_unterminated=None,
            blocks=[
                RichTextPromptBlock(
                    block_type="RICH_TEXT",
                    state=None,
                    cache_config=None,
                    blocks=[
                        PlainTextPromptBlock(
                            block_type="PLAIN_TEXT", state=None, cache_config=None, text="second message"
                        ),
                        PlainTextPromptBlock(
                            block_type="PLAIN_TEXT", state=None, cache_config=None, text="third message"
                        ),
                    ],
                )
            ],
        ),
        VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
    ]


def test_get_mcp_tool_name_snake_case():
    """Test MCPToolDefinition function name generation with snake case."""
    mcp_tool = MCPToolDefinition(
        name="create_repository",
        server=MCPServer(name="Github Server", url="https://api.github.com"),
        parameters={"repository_name": "string", "description": "string"},
    )

    result = get_mcp_tool_name(mcp_tool)
    assert result == "github_server__create_repository"


def test_create_tool_prompt_node_settings_dict_stream_disabled(vellum_adhoc_prompt_client):
    # GIVEN settings provided as dict with stream disabled
    tool_prompt_node = create_tool_prompt_node(
        ml_model="gpt-4o-mini",
        blocks=[],
        functions=[],
        prompt_inputs=None,
        parameters=DEFAULT_PROMPT_PARAMETERS,
        max_prompt_iterations=1,
        settings={"stream_enabled": False},
    )

    # AND the API mocks
    def generate_non_stream_response(*args, **kwargs):
        return FulfilledExecutePromptEvent(execution_id=str(uuid4()), outputs=[StringVellumValue(value="ok")])

    vellum_adhoc_prompt_client.adhoc_execute_prompt.side_effect = generate_non_stream_response

    # WHEN we run the node
    node_instance = tool_prompt_node()
    list(node_instance.run())

    # THEN the node should have called the API correctly
    assert node_instance.settings is not None
    assert node_instance.settings.stream_enabled is False
    assert vellum_adhoc_prompt_client.adhoc_execute_prompt.call_count == 1
    assert vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count == 0


def test_create_tool_prompt_node_settings_model_stream_enabled(vellum_adhoc_prompt_client):
    # GIVEN settings provided as PromptSettings with stream enabled
    tool_prompt_node = create_tool_prompt_node(
        ml_model="gpt-4o-mini",
        blocks=[],
        functions=[],
        prompt_inputs=None,
        parameters=DEFAULT_PROMPT_PARAMETERS,
        max_prompt_iterations=1,
        settings=PromptSettings(stream_enabled=True),
    )

    # AND the API mocks
    def generate_stream_events(*args, **kwargs):
        execution_id = str(uuid4())
        events = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(execution_id=execution_id, outputs=[StringVellumValue(value="ok")]),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_stream_events

    # WHEN we run the node
    node_instance = tool_prompt_node()
    list(node_instance.run())

    # THEN the node should have called the API correctly
    assert node_instance.settings is not None
    assert node_instance.settings.stream_enabled is True
    assert vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count == 1
    assert vellum_adhoc_prompt_client.adhoc_execute_prompt.call_count == 0
