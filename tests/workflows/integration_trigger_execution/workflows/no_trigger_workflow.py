"""Workflow without IntegrationTrigger for testing error cases."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState


class SimpleNodeNoTrigger(BaseNode):
    """Simple node without trigger dependencies."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="No trigger workflow")


class NoTriggerWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Workflow without any triggers."""

    graph = SimpleNodeNoTrigger

    class Outputs(BaseWorkflow.Outputs):
        result = SimpleNodeNoTrigger.Outputs.result
