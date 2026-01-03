from vellum.client.types import VellumDocument
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    document: VellumDocument
    name: str


class PassthroughNode(BaseNode[BaseState]):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="done")


class InvalidPdfDataUrlWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = PassthroughNode

    class Outputs(BaseWorkflow.Outputs):
        final_result = PassthroughNode.Outputs.result
