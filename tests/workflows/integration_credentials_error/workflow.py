from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class IntegrationActionNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        vellum_client = self._context.vellum_client
        result = vellum_client.integrations.execute_integration_tool(
            integration_name="GITHUB",
            integration_provider="COMPOSIO",
            tool_name="GITHUB_CREATE_AN_ISSUE",
            arguments={"repo": "user/repo", "title": "Test Issue"},
        )
        return self.Outputs(result=str(result))


class IntegrationCredentialsErrorWorkflow(BaseWorkflow):
    graph = IntegrationActionNode

    class Outputs(BaseWorkflow.Outputs):
        result = IntegrationActionNode.Outputs.result
