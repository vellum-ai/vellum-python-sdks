from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    transcript: str


class SimpleNode(BaseNode):
    transcript = Inputs.transcript

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> BaseOutputs:
        return self.Outputs(result=f"Processed: {self.transcript}")


class TestRequiredInputsNoTriggerWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = SimpleNode

    class Outputs(BaseOutputs):
        final_result = SimpleNode.Outputs.result
