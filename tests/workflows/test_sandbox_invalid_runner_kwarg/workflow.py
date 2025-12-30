from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    message: str


class ProcessNode(BaseNode[BaseState]):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="processed")


class InvalidRunnerKwargWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ProcessNode

    class Outputs(BaseWorkflow.Outputs):
        final_result = ProcessNode.Outputs.result
