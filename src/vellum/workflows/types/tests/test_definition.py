import pytest
from uuid import UUID

from vellum.client.types.vellum_secret import VellumSecret
from vellum.workflows.constants import AuthorizationType
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.types.definition import ComposioToolDefinition, DeploymentDefinition, MCPServer, MCPToolDefinition


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
    assert composio_tool.name == "github_create_an_issue"


@pytest.mark.parametrize(
    "authorization_type, bearer_token_value, api_key_header_key, api_key_header_value",
    [
        (
            AuthorizationType.BEARER_TOKEN,
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            None,
            None,
        ),
        (
            AuthorizationType.BEARER_TOKEN,
            EnvironmentVariableReference(name="GITHUB_PERSONAL_ACCESS_TOKEN"),
            None,
            None,
        ),
        (
            AuthorizationType.API_KEY,
            None,
            "API_KEY",
            VellumSecret(name="GITHUB_PERSONAL_ACCESS_TOKEN"),
        ),
    ],
    ids=[
        "bearer_token_string",
        "bearer_token_environment_variable",
        "api_key_header",
    ],
)
def test_mcp_tool_definition_creation(
    authorization_type,
    bearer_token_value,
    api_key_header_key,
    api_key_header_value,
):
    """Test that MCPToolDefinition can be created with required fields."""
    mcp_tool = MCPToolDefinition(
        name="create_repository",
        server=MCPServer(
            name="github",
            url="https://api.githubcopilot.com/mcp/",
            authorization_type=authorization_type,
            bearer_token_value=bearer_token_value,
            api_key_header_key=api_key_header_key,
            api_key_header_value=api_key_header_value,
        ),
        parameters={"repository_name": "string", "description": "string"},
    )

    assert mcp_tool.name == "create_repository"
    assert mcp_tool.server.name == "github"
    assert mcp_tool.server.url == "https://api.githubcopilot.com/mcp/"
    assert mcp_tool.server.authorization_type == authorization_type
    assert mcp_tool.parameters == {"repository_name": "string", "description": "string"}

    if authorization_type == AuthorizationType.BEARER_TOKEN:
        if isinstance(bearer_token_value, EnvironmentVariableReference):
            assert mcp_tool.server.bearer_token_value.name == bearer_token_value.name
        else:
            assert mcp_tool.server.bearer_token_value == bearer_token_value
        assert mcp_tool.server.api_key_header_key is None
        assert mcp_tool.server.api_key_header_value is None
    elif authorization_type == AuthorizationType.API_KEY:
        assert mcp_tool.server.bearer_token_value is None
        assert mcp_tool.server.api_key_header_key == api_key_header_key
        assert mcp_tool.server.api_key_header_value == api_key_header_value
