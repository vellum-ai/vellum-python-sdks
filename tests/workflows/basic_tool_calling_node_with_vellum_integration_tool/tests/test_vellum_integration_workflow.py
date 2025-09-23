from unittest.mock import MagicMock, patch

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.types.definition import VellumIntegrationToolDefinition


def test_vellum_integration_tool_definition_serialization():
    """Test that VellumIntegrationToolDefinition serializes with correct discriminator."""
    tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration="GITHUB",
        name="GITHUB_CREATE_AN_ISSUE",
        description="Create a new issue in a GitHub repository",
    )

    serialized = tool.model_dump()

    assert serialized["type"] == "VELLUM_INTEGRATION"
    assert serialized["provider"] == VellumIntegrationProviderType.COMPOSIO
    assert serialized["integration"] == "GITHUB"
    assert serialized["name"] == "GITHUB_CREATE_AN_ISSUE"
    assert serialized["description"] == "Create a new issue in a GitHub repository"


def test_vellum_integration_tool_definition_deserialization():
    """Test that VellumIntegrationToolDefinition deserializes correctly."""
    data = {
        "type": "VELLUM_INTEGRATION",
        "provider": "COMPOSIO",
        "integration": "GITHUB",
        "name": "GITHUB_CREATE_AN_ISSUE",
        "description": "Create a new issue in a GitHub repository",
    }

    tool = VellumIntegrationToolDefinition(**data)

    assert tool.type == "VELLUM_INTEGRATION"
    assert tool.provider == VellumIntegrationProviderType.COMPOSIO
    assert tool.integration == "GITHUB"
    assert tool.name == "GITHUB_CREATE_AN_ISSUE"
    assert tool.description == "Create a new issue in a GitHub repository"


@patch("vellum.workflows.integrations.vellum_integration_service.create_vellum_client")
def test_workflow_with_vellum_integration_tool(mock_create_client):
    """Test that a workflow with VellumIntegrationToolDefinition works correctly."""
    # Mock the Vellum client
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock the tool definition retrieval
    mock_client.integrations.retrieve_integration_tool_definition.return_value = MagicMock(
        name="GITHUB_CREATE_AN_ISSUE",
        description="Create a new issue in a GitHub repository",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Issue title"},
                "body": {"type": "string", "description": "Issue body"},
            },
            "required": ["title"],
        },
        provider="COMPOSIO",
    )

    # Verify the tool is properly configured
    from tests.workflows.basic_tool_calling_node_with_vellum_integration_tool.workflow import (
        github_create_issue_vellum_tool,
    )

    tool = github_create_issue_vellum_tool
    assert isinstance(tool, VellumIntegrationToolDefinition)
    assert tool.type == "VELLUM_INTEGRATION"
    assert tool.provider == VellumIntegrationProviderType.COMPOSIO
    assert tool.integration == "GITHUB"
    assert tool.name == "GITHUB_CREATE_AN_ISSUE"
