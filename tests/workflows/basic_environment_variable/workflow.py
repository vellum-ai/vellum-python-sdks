from vellum.workflows.environment import EnvironmentVariables
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow


class ReferenceEnvironmentNode(BaseNode):
    url = EnvironmentVariables.get("API_URL", "https://default.api.vellum.ai")

    class Outputs(BaseNode.Outputs):
        url: str

    def run(self) -> Outputs:
        return self.Outputs(url=self.url)


class BasicEnvironmentVariableWorkflow(BaseWorkflow):
    graph = ReferenceEnvironmentNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = ReferenceEnvironmentNode.Outputs.url
