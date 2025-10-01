import pytest
from uuid import UUID

from vellum.workflows.constants import AuthorizationType, VellumIntegrationProviderType
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.types.definition import (
    ComposioToolDefinition,
    DeploymentDefinition,
    MCPServer,
    MCPToolDefinition,
    VellumIntegrationToolDefinition,
)


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
        toolkit="GITHUB",
        action="GITHUB_CREATE_AN_ISSUE",
        description="Create a new issue in a GitHub repository",
        user_id=None,
    )

    assert composio_tool.toolkit == "GITHUB"
    assert composio_tool.action == "GITHUB_CREATE_AN_ISSUE"
    assert composio_tool.description == "Create a new issue in a GitHub repository"
    assert composio_tool.user_id is None
    assert composio_tool.name == "github_create_an_issue"


def test_mcp_tool_definition_creation_bearer_token():
    """Test that MCPToolDefinition can be created with required fields."""
    mcp_tool = MCPToolDefinition(
        name="create_repository",
        server=MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            authorization_type=AuthorizationType.BEARER_TOKEN,
            bearer_token_value=EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN"),
        ),
        parameters={
            "type": "object",
            "properties": {
                "repository_name": {"type": "string", "description": "Repository name"},
                "description": {"type": "string", "description": "Repository description"},
            },
            "required": ["repository_name"],
        },
    )

    assert mcp_tool.name == "create_repository"
    assert mcp_tool.server.name == "github"
    assert mcp_tool.server.url == "https://api.githubcopilot.com/mcp/"
    assert mcp_tool.server.authorization_type == AuthorizationType.BEARER_TOKEN
    assert mcp_tool.parameters == {
        "type": "object",
        "properties": {
            "repository_name": {"type": "string", "description": "Repository name"},
            "description": {"type": "string", "description": "Repository description"},
        },
        "required": ["repository_name"],
    }

    assert isinstance(mcp_tool.server.bearer_token_value, EnvironmentVariableReference)
    assert mcp_tool.server.bearer_token_value.name == "GITHUB_PERSONAL_ACCESS_TOKEN"


def test_mcp_tool_definition_creation_api_key():
    """Test that MCPToolDefinition can be created with required fields."""
    mcp_tool = MCPToolDefinition(
        name="create_repository",
        server=MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            authorization_type=AuthorizationType.API_KEY,
            api_key_header_key="Authorization",
            api_key_header_value=EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN"),
        ),
        parameters={
            "type": "object",
            "properties": {
                "repository_name": {"type": "string", "description": "Repository name"},
                "description": {"type": "string", "description": "Repository description"},
            },
            "required": ["repository_name"],
        },
    )

    assert mcp_tool.name == "create_repository"
    assert mcp_tool.server.name == "github"
    assert mcp_tool.server.url == "https://api.githubcopilot.com/mcp/"
    assert mcp_tool.server.authorization_type == AuthorizationType.API_KEY
    assert mcp_tool.server.api_key_header_key == "Authorization"
    assert isinstance(mcp_tool.server.api_key_header_value, EnvironmentVariableReference)
    assert mcp_tool.server.api_key_header_value.name == "GITHUB_PERSONAL_ACCESS_TOKEN"
    assert mcp_tool.parameters == {
        "type": "object",
        "properties": {
            "repository_name": {"type": "string", "description": "Repository name"},
            "description": {"type": "string", "description": "Repository description"},
        },
        "required": ["repository_name"],
    }


def test_mcp_tool_definition_creation_no_authorization():
    """Test that MCPToolDefinition can be created with no authorization."""
    mcp_tool = MCPToolDefinition(
        name="create_repository",
        server=MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
        ),
    )

    assert mcp_tool.name == "create_repository"
    assert mcp_tool.server.name == "github"
    assert mcp_tool.server.url == "https://api.githubcopilot.com/mcp/"
    assert mcp_tool.server.authorization_type is None
    assert mcp_tool.server.bearer_token_value is None
    assert mcp_tool.server.api_key_header_key is None
    assert mcp_tool.server.api_key_header_value is None


def test_vellum_integration_tool_definition_creation():
    """Test that VellumIntegrationToolDefinition can be created with required fields."""
    vellum_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="GITHUB",
        name="create_issue",
        description="Create a new issue in a GitHub repository",
    )

    assert vellum_tool.type == "VELLUM_INTEGRATION"
    assert vellum_tool.provider == VellumIntegrationProviderType.COMPOSIO
    assert vellum_tool.integration_name == "GITHUB"
    assert vellum_tool.name == "create_issue"
    assert vellum_tool.description == "Create a new issue in a GitHub repository"


def test_vellum_integration_tool_definition_with_different_provider():
    """Test VellumIntegrationToolDefinition with a different provider."""
    vellum_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration_name="SLACK",
        name="send_message",
        description="Send a message to a Slack channel",
    )

    assert vellum_tool.type == "VELLUM_INTEGRATION"
    assert vellum_tool.provider == VellumIntegrationProviderType.COMPOSIO
    assert vellum_tool.integration_name == "SLACK"
    assert vellum_tool.name == "send_message"
    assert vellum_tool.description == "Send a message to a Slack channel"
