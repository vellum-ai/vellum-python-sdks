from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.api_node import APINode
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    pass


class State(BaseState):
    pass


class VellumAPINode(APINode):
    url = ""  # Empty URL will cause validation error

    def run(self) -> APINode.Outputs:
        return super().run()


class CustomAPINode(APINode):
    def run(self) -> APINode.Outputs:
        raise Exception("User configuration error: Invalid API endpoint")


class VellumErrorWorkflow(BaseWorkflow[Inputs, State]):
    graph = VellumAPINode

    class Outputs(BaseWorkflow.Outputs):
        final_value = VellumAPINode.Outputs.json


class CustomErrorWorkflow(BaseWorkflow[Inputs, State]):
    graph = CustomAPINode

    class Outputs(BaseWorkflow.Outputs):
        final_value = CustomAPINode.Outputs.json
