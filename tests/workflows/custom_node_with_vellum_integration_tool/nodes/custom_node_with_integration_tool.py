from vellum.workflows import BaseNode
from vellum.workflows.types.definition import VellumIntegrationToolDefinition


class CustomNodeWithIntegrationTool(BaseNode):
    tool = VellumIntegrationToolDefinition(
        provider="COMPOSIO",
        integration_name="GITHUB",
        name="create_issue",
        description="Create a new issue in a GitHub repository",
    )
