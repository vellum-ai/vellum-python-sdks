from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.conditional_node import ConditionalNode
from .nodes.final_output import FinalOutput


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = ConditionalNode.Ports.branch_1 >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
