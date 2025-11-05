from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core import ErrorNode
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    threshold: int


class StartNode(BaseNode):
    class Ports(BaseNode.Ports):
        success = Port.on_if(Inputs.threshold.greater_than(10))
        fail = Port.on_else()


class SuccessNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result = Inputs.threshold


class FailNode(ErrorNode):
    error = "Input threshold was too low"


class BasicErrorNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    """
    A simple workflow that demonstrates how to use an error node.
    """

    graph = {
        StartNode.Ports.success >> SuccessNode,
        StartNode.Ports.fail >> FailNode,
    }

    class Outputs(BaseWorkflow.Outputs):
        final_value = SuccessNode.Outputs.result
