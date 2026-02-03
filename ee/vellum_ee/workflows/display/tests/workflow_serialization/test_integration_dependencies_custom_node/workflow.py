from typing import Any

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class FetchNotionBlock(BaseNode):
    """A custom node that calls execute_integration_tool with a single integration."""

    block_id: str = "test-block-id"

    class Outputs(BaseNode.Outputs):
        contents: Any

    def run(self) -> BaseNode.Outputs:
        client = self._context.vellum_client
        response = client.integrations.execute_integration_tool(
            integration_name="NOTION",
            integration_provider="COMPOSIO",
            tool_name="NOTION_FETCH_BLOCK_CONTENTS",
            arguments={"block_id": self.block_id},
            toolkit_version="20260203_00",
        )
        return self.Outputs(contents=response.data)


class SingleIntegrationInputs(BaseInputs):
    pass


class SingleIntegrationWorkflow(BaseWorkflow[SingleIntegrationInputs, BaseState]):
    """Workflow with a single custom node that uses one integration."""

    graph = FetchNotionBlock

    class Outputs(BaseWorkflow.Outputs):
        contents = FetchNotionBlock.Outputs.contents


class MultiIntegrationNode(BaseNode):
    """A custom node that calls execute_integration_tool multiple times with different integrations."""

    class Outputs(BaseNode.Outputs):
        result: Any

    def run(self) -> BaseNode.Outputs:
        client = self._context.vellum_client
        client.integrations.execute_integration_tool(
            integration_name="GITHUB",
            integration_provider="COMPOSIO",
            tool_name="GITHUB_CREATE_ISSUE",
            arguments={},
        )
        client.integrations.execute_integration_tool(
            integration_name="SLACK",
            integration_provider="COMPOSIO",
            tool_name="SLACK_SEND_MESSAGE",
            arguments={},
        )
        return self.Outputs(result="done")


class MultiIntegrationInputs(BaseInputs):
    pass


class MultiIntegrationWorkflow(BaseWorkflow[MultiIntegrationInputs, BaseState]):
    """Workflow with a custom node that uses multiple integrations."""

    graph = MultiIntegrationNode

    class Outputs(BaseWorkflow.Outputs):
        result = MultiIntegrationNode.Outputs.result
