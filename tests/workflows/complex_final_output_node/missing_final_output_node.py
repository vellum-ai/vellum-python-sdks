from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    alpha: str
    beta: str


class FirstFinalOutputNode(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = Inputs.alpha


class PassthroughNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value = Inputs.beta


class MissingFinalOutputNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = {FirstFinalOutputNode, PassthroughNode}

    class Outputs(BaseWorkflow.Outputs):
        alpha = FirstFinalOutputNode.Outputs.value
        beta = PassthroughNode.Outputs.value
