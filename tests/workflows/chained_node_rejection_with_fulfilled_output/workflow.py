from vellum.workflows import BaseWorkflow
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode


class FirstNode(BaseNode):
    """A node that succeeds and produces an output."""

    class Outputs(BaseNode.Outputs):
        value: str = "success"


class SecondNode(BaseNode):
    """A node that fails after the first node succeeds."""

    first_value = FirstNode.Outputs.value

    class Outputs(BaseNode.Outputs):
        pass

    def run(self) -> Outputs:
        raise NodeException(code=WorkflowErrorCode.USER_DEFINED_ERROR, message="Second node failed")


class ChainedNodeRejectionWithFulfilledOutputWorkflow(BaseWorkflow):
    """
    A workflow with two chained nodes where:
    - The first node succeeds and produces an output
    - The second node fails
    - The workflow output points to the first node's output

    This tests that the workflow should be rejected (not fulfilled) when any node fails,
    even if the workflow output was already resolved from a successful node.
    """

    graph = FirstNode >> SecondNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = FirstNode.Outputs.value
