from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    pass


class State(BaseState):
    pass


class VellumNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        raise Exception("An unexpected error occurred while running node")


class CustomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        raise Exception("An unexpected error occurred while running node")


class VellumErrorWorkflow(BaseWorkflow[Inputs, State]):
    graph = VellumNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = VellumNode.Outputs.result


class CustomErrorWorkflow(BaseWorkflow[Inputs, State]):
    graph = CustomNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = CustomNode.Outputs.result
