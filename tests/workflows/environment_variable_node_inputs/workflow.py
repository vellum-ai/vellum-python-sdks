from vellum.workflows.environment import EnvironmentVariables
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow


class NodeWithEnvironmentVariable(BaseNode):
    api_key = EnvironmentVariables.get("TEST_API_KEY")

    class Outputs(BaseNode.Outputs):
        api_key: str

    def run(self) -> Outputs:
        return self.Outputs(api_key=self.api_key)


class EnvironmentVariableNodeInputsWorkflow(BaseWorkflow):
    graph = NodeWithEnvironmentVariable

    class Outputs(BaseWorkflow.Outputs):
        final_value = NodeWithEnvironmentVariable.Outputs.api_key
