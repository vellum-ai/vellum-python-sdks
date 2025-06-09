from vellum.workflows.environment import EnvironmentVariables
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow


class OptionalDefaultEnvironmentNode(BaseNode):
    url = EnvironmentVariables.get("MISSING_ENV_VAR")

    class Outputs(BaseNode.Outputs):
        url: str

    def run(self) -> Outputs:
        return self.Outputs(url=self.url)


class OptionalDefaultEnvironmentVariableWorkflow(BaseWorkflow):
    graph = OptionalDefaultEnvironmentNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = OptionalDefaultEnvironmentNode.Outputs.url
