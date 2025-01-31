from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.final_output import FinalOutput
from .nodes.templating_node import TemplatingNode


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = TemplatingNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
