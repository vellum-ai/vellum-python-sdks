from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.api_node import APINode
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    pass


class State(BaseState):
    pass


class VellumAPINode(APINode):
    pass


class CustomAPINode(BaseNode):
    class Outputs(BaseNode.Outputs):
        json: dict

    def run(self) -> BaseNode.Outputs:
        raise Exception("User defined error")


class VellumErrorWorkflow(BaseWorkflow[Inputs, State]):
    graph = VellumAPINode

    class Outputs(BaseWorkflow.Outputs):
        final_value = VellumAPINode.Outputs.json


class CustomErrorWorkflow(BaseWorkflow[Inputs, State]):
    graph = CustomAPINode

    class Outputs(BaseWorkflow.Outputs):
        final_value = CustomAPINode.Outputs.json
