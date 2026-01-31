from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.final_output import FinalOutput
from .nodes.simple_node import SimpleNode
from .triggers.manual import Manual


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = Manual >> SimpleNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
