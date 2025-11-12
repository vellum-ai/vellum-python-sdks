from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import undefined
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState


class UndefinedOutputNode(BaseNode):
    """Node that returns an undefined output."""

    class Outputs(BaseNode.Outputs):
        result = undefined

    def run(self) -> Outputs:
        return self.Outputs()


class JsonAccessNode(FinalOutputNode[BaseState, str]):
    """Node that tries to perform JSON string access on the undefined output."""

    class Outputs(FinalOutputNode.Outputs):
        value = UndefinedOutputNode.Outputs.result["field"]  # type: ignore


class UndefinedOutputJsonAccessWorkflow(BaseWorkflow):
    """Workflow that tests accessing a field on an undefined output."""

    graph = UndefinedOutputNode >> JsonAccessNode

    class Outputs(BaseWorkflow.Outputs):
        output = JsonAccessNode.Outputs.value
