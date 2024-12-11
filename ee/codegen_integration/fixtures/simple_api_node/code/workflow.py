from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.api_node import ApiNode
from .nodes.final_output import FinalOutput


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = ApiNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
