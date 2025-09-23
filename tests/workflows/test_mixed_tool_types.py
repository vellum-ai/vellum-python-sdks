"""Test mixed tool types (COMPOSIO and VELLUM_INTEGRATION) working together."""

from typing import List

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.types.core import ToolBase
from vellum.workflows.types.definition import ComposioToolDefinition, VellumIntegrationToolDefinition


def test_mixed_tool_types_serialization():
    """Test that both COMPOSIO and VELLUM_INTEGRATION tools can coexist and serialize correctly."""

    # Create a COMPOSIO tool
    composio_tool = ComposioToolDefinition(
        toolkit="GITHUB",
        action="GITHUB_CREATE_AN_ISSUE",
        description="Create a GitHub issue via Composio",
        user_id=None,
    )

    # Create a VELLUM_INTEGRATION tool
    vellum_integration_tool = VellumIntegrationToolDefinition(
        provider=VellumIntegrationProviderType.COMPOSIO,
        integration="SLACK",
        name="SLACK_SEND_MESSAGE",
        description="Send a Slack message via Vellum Integration",
    )

    # Create a list of mixed tools (as would be used in a ToolCallingNode)
    tools: List[ToolBase] = [composio_tool, vellum_integration_tool]

    # Serialize each tool and verify their discriminators
    composio_serialized = composio_tool.model_dump()
    vellum_serialized = vellum_integration_tool.model_dump()

    # Verify COMPOSIO tool serialization
    assert composio_serialized["type"] == "COMPOSIO"
    assert composio_serialized["toolkit"] == "GITHUB"
    assert composio_serialized["action"] == "GITHUB_CREATE_AN_ISSUE"
    assert composio_serialized["description"] == "Create a GitHub issue via Composio"
    assert composio_serialized["user_id"] is None
    assert composio_serialized["name"] == "github_create_an_issue"

    # Verify VELLUM_INTEGRATION tool serialization
    assert vellum_serialized["type"] == "VELLUM_INTEGRATION"
    assert vellum_serialized["provider"] == VellumIntegrationProviderType.COMPOSIO
    assert vellum_serialized["integration"] == "SLACK"
    assert vellum_serialized["name"] == "SLACK_SEND_MESSAGE"
    assert vellum_serialized["description"] == "Send a Slack message via Vellum Integration"

    # Verify that both tools can be in the same list without issues
    assert len(tools) == 2
    assert isinstance(tools[0], ComposioToolDefinition)
    assert isinstance(tools[1], VellumIntegrationToolDefinition)


def test_mixed_tool_types_deserialization():
    """Test that both tool types can be deserialized from JSON correctly."""

    # JSON representation of COMPOSIO tool
    composio_data = {
        "type": "COMPOSIO",
        "toolkit": "GITHUB",
        "action": "GITHUB_CREATE_AN_ISSUE",
        "description": "Create a GitHub issue via Composio",
        "user_id": None,
        "name": "github_create_an_issue",
    }

    # JSON representation of VELLUM_INTEGRATION tool
    vellum_data = {
        "type": "VELLUM_INTEGRATION",
        "provider": "COMPOSIO",
        "integration": "SLACK",
        "name": "SLACK_SEND_MESSAGE",
        "description": "Send a Slack message via Vellum Integration",
    }

    # Deserialize COMPOSIO tool
    composio_tool = ComposioToolDefinition(**composio_data)
    assert composio_tool.type == "COMPOSIO"
    assert composio_tool.toolkit == "GITHUB"
    assert composio_tool.action == "GITHUB_CREATE_AN_ISSUE"

    # Deserialize VELLUM_INTEGRATION tool
    vellum_tool = VellumIntegrationToolDefinition(**vellum_data)
    assert vellum_tool.type == "VELLUM_INTEGRATION"
    assert vellum_tool.provider == VellumIntegrationProviderType.COMPOSIO
    assert vellum_tool.integration == "SLACK"
    assert vellum_tool.name == "SLACK_SEND_MESSAGE"


def test_tool_type_discrimination():
    """Test that tool types can be properly discriminated based on their type field."""

    tool_configs = [
        {
            "type": "COMPOSIO",
            "toolkit": "GITHUB",
            "action": "GITHUB_CREATE_AN_ISSUE",
            "description": "Create issue",
            "user_id": None,
            "name": "github_create_an_issue",
        },
        {
            "type": "VELLUM_INTEGRATION",
            "provider": "COMPOSIO",
            "integration": "SLACK",
            "name": "SLACK_SEND_MESSAGE",
            "description": "Send message",
        },
    ]

    # Process each tool config and instantiate the correct type
    tools = []
    for config in tool_configs:
        if config["type"] == "COMPOSIO":
            tool = ComposioToolDefinition(**config)
        elif config["type"] == "VELLUM_INTEGRATION":
            tool = VellumIntegrationToolDefinition(**config)
        else:
            raise ValueError(f"Unknown tool type: {config['type']}")
        tools.append(tool)

    # Verify we got the right types
    assert len(tools) == 2
    assert isinstance(tools[0], ComposioToolDefinition)
    assert isinstance(tools[1], VellumIntegrationToolDefinition)
    assert tools[0].type == "COMPOSIO"
    assert tools[1].type == "VELLUM_INTEGRATION"
