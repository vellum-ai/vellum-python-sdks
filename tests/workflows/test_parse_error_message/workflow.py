from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow


class Inputs(BaseInputs):
    integration_name: str
    tool_name: str


class IntegrationToolErrorNode(BaseNode[BaseState]):
    """
    A node that calls execute_integration_tool to test _parse_error_message logic.

    This node directly calls the Vellum client's execute_integration_tool method
    without catching exceptions, allowing errors to propagate naturally to the
    WorkflowRunner where _parse_error_message can be tested.
    """

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        vellum_client = self._context.vellum_client
        workflow_inputs = self.state.meta.workflow_inputs
        assert isinstance(workflow_inputs, Inputs)
        result = vellum_client.integrations.execute_integration_tool(
            integration_name=workflow_inputs.integration_name,
            integration_provider="COMPOSIO",
            tool_name=workflow_inputs.tool_name,
            arguments={},
        )
        return self.Outputs(result=str(result))


class ParseErrorMessageTestWorkflow(BaseWorkflow[Inputs, BaseState]):
    """A workflow that tests the _parse_error_message logic."""

    graph = IntegrationToolErrorNode

    class Outputs(BaseWorkflow.Outputs):
        result = IntegrationToolErrorNode.Outputs.result
