from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    message: str


class CodeExecution(BaseNode[BaseState]):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="executed")


class InvalidMocksReferenceWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = CodeExecution

    class Outputs(BaseWorkflow.Outputs):
        final_result = CodeExecution.Outputs.result
