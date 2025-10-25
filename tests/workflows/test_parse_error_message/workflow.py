from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseInputs, BaseWorkflow


class Inputs(BaseInputs):
    value: str


class ErrorNode(BaseNode[BaseState]):
    """A node that raises a generic exception to test _parse_error_message logic."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        raise ValueError("Test error from node")


class ParseErrorMessageTestWorkflow(BaseWorkflow[Inputs, BaseState]):
    """A workflow that tests the _parse_error_message logic."""

    graph = ErrorNode

    class Outputs(BaseWorkflow.Outputs):
        result = ErrorNode.Outputs.result
