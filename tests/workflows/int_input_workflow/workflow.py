from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    list_id: int


class IntOutputNode(FinalOutputNode[BaseState, int]):
    class Outputs(FinalOutputNode.Outputs):
        value = Inputs.list_id


class IntInputWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = IntOutputNode

    class Outputs(BaseWorkflow.Outputs):
        value = IntOutputNode.Outputs.value
