"""Workflow with only ManualTrigger (no IntegrationTrigger) for negative testing."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class SimpleNode(BaseNode):
    """Simple node that doesn't reference any trigger attributes."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="No trigger workflow")


class NoTriggerWorkflow(BaseWorkflow):
    """Workflow without IntegrationTrigger - uses implicit ManualTrigger."""

    graph = SimpleNode

    class Outputs(BaseWorkflow.Outputs):
        result = SimpleNode.Outputs.result
