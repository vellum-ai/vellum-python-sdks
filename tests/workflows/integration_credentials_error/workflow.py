from typing import Any, Dict

from vellum.workflows import BaseWorkflow
from vellum.workflows.integrations.vellum_integration_service import VellumIntegrationService
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.vellum_client import create_vellum_client


class IntegrationActionNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: Dict[str, Any]

    def run(self) -> Outputs:
        vellum_client = create_vellum_client()
        service = VellumIntegrationService(client=vellum_client)
        result = service.execute_tool(
            integration="GITHUB",
            provider="COMPOSIO",
            tool_name="GITHUB_CREATE_AN_ISSUE",
            arguments={"repo": "user/repo", "title": "Test Issue"},
        )
        return self.Outputs(result=result)


class IntegrationCredentialsErrorWorkflow(BaseWorkflow):
    graph = IntegrationActionNode

    class Outputs(BaseWorkflow.Outputs):
        result = IntegrationActionNode.Outputs.result
