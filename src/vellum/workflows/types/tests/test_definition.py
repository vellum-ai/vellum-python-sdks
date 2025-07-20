import pytest
from uuid import UUID

from vellum.workflows.types.definition import ComposioToolDefinition, DeploymentDefinition


@pytest.mark.parametrize(
    "deployment_value, expected_deployment_id, expected_deployment_name",
    [
        # Valid UUID string
        (
            "57f09beb-b463-40e0-bf9e-c972e664352f",
            UUID("57f09beb-b463-40e0-bf9e-c972e664352f"),
            None,
        ),
        # Name string
        (
            "tool-calling-subworkflow",
            None,
            "tool-calling-subworkflow",
        ),
    ],
    ids=[
        "valid_uuid",
        "valid_name",
    ],
)
def test_deployment_definition(deployment_value, expected_deployment_id, expected_deployment_name):
    """Test that DeploymentDefinition properties correctly identify and extract UUID vs name."""
    deployment = DeploymentDefinition(deployment=deployment_value)

    assert deployment.deployment_id == expected_deployment_id
    assert deployment.deployment_name == expected_deployment_name


def test_composio_tool_definition_creation():
    """Test that ComposioToolDefinition can be created with required fields."""
    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )

    assert composio_tool.toolkit == "GITHUB"
    assert composio_tool.action == "GITHUB_CREATE_AN_ISSUE"
    assert composio_tool.description == "Create a new issue in a GitHub repository"
    assert composio_tool.display_name is None


def test_composio_tool_definition_with_optional_fields():
    """Test that ComposioToolDefinition can be created with optional fields."""
    composio_tool = ComposioToolDefinition(
        toolkit="SLACK",
        action="SLACK_SEND_MESSAGE",
        description="Send a message to a Slack channel",
        display_name="Send Slack Message",
    )

    assert composio_tool.toolkit == "SLACK"
    assert composio_tool.action == "SLACK_SEND_MESSAGE"
    assert composio_tool.description == "Send a message to a Slack channel"
    assert composio_tool.display_name == "Send Slack Message"


@pytest.mark.parametrize(
    "toolkit, action, expected_name",
    [
        ("GITHUB", "GITHUB_CREATE_AN_ISSUE", "github_github_create_an_issue"),
        ("SLACK", "SLACK_SEND_MESSAGE", "slack_slack_send_message"),
        ("GMAIL", "GMAIL_CREATE_EMAIL_DRAFT", "gmail_gmail_create_email_draft"),
        ("NOTION", "NOTION_CREATE_PAGE", "notion_notion_create_page"),
    ],
    ids=[
        "github_action",
        "slack_action",
        "gmail_action",
        "notion_action",
    ],
)
def test_composio_tool_definition_name_property(toolkit, action, expected_name):
    """Test that ComposioToolDefinition name property generates correct function names."""
    composio_tool = ComposioToolDefinition(toolkit=toolkit, action=action, description="Test description")

    assert composio_tool.name == expected_name


def test_composio_tool_definition_json_serialization():
    """Test that ComposioToolDefinition serializes correctly to JSON."""
    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB",
        action="GITHUB_CREATE_AN_ISSUE",
        description="Create a new issue in a GitHub repository",
        display_name="Create GitHub Issue",
    )

    json_data = composio_tool.model_dump(mode="json")

    # Check that all expected fields are present
    assert json_data["type"] == "COMPOSIO"
    assert json_data["toolkit"] == "GITHUB"
    assert json_data["action"] == "GITHUB_CREATE_AN_ISSUE"
    assert json_data["description"] == "Create a new issue in a GitHub repository"
    assert json_data["display_name"] == "Create GitHub Issue"
    assert json_data["name"] == "github_github_create_an_issue"


def test_composio_tool_definition_python_serialization():
    """Test that ComposioToolDefinition serializes correctly in Python mode (no type field)."""
    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )

    python_data = composio_tool.model_dump(mode="python")

    # Check that type and name fields are NOT added in python mode
    assert "type" not in python_data
    assert "name" not in python_data
    assert python_data["toolkit"] == "GITHUB"
    assert python_data["action"] == "GITHUB_CREATE_AN_ISSUE"
    assert python_data["description"] == "Create a new issue in a GitHub repository"
    assert python_data["display_name"] is None


def test_composio_tool_definition_default_serialization():
    """Test that ComposioToolDefinition default serialization mode is python."""
    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )

    default_data = composio_tool.model_dump()

    # Default should be python mode, so no type/name fields
    assert "type" not in default_data
    assert "name" not in default_data
    assert default_data["toolkit"] == "GITHUB"
