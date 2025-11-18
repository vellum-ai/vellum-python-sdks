from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    message: str


class SimpleNode(BaseNode):
    message = Inputs.message

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> BaseOutputs:
        return self.Outputs(result=f"Hello {self.message}")


class TestBaseInputsWithMetadataWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = SimpleNode

    class Outputs(BaseOutputs):
        final_result = SimpleNode.Outputs.result
