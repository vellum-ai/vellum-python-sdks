from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    input: str


class BasicGenericNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


class BasicGenericNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    _enable_auto_layout = True
    graph = BasicGenericNode

    class Outputs(BaseWorkflow.Outputs):
        output = BasicGenericNode.Outputs.output
