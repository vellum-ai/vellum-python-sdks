from typing import Any, Dict

from vellum.workflows import BaseNode
from vellum.workflows.types.definition import VellumIntegrationToolDefinition


class CustomNodeWithIntegrationTool(BaseNode):
    tool = VellumIntegrationToolDefinition(
        provider="COMPOSIO",
        integration_name="GITHUB",
        name="create_issue",
        description="Create a new issue in a GitHub repository",
    )

    class Outputs(BaseNode.Outputs):
        result: Dict[str, Any]

    def run(self) -> Outputs:
        response = self._context.vellum_client.integrations.execute_integration_tool(
            integration_name=self.tool.integration_name,
            integration_provider=self.tool.provider,
            tool_name=self.tool.name,
            arguments={},
        )
        return self.Outputs(result=response.data)
