from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    message: str


class UsedNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="executed")


class OrphanNodeInNodesDir(BaseWorkflow[Inputs, BaseState]):
    graph = UsedNode

    class Outputs(BaseWorkflow.Outputs):
        final_result = UsedNode.Outputs.result
