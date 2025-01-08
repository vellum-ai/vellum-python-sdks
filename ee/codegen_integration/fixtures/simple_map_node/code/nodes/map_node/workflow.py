from vellum.workflows import BaseWorkflow
from vellum.workflows.state import BaseState

from .inputs import Inputs
from .nodes.final_output import FinalOutput
from .nodes.search_node import SearchNode
from .nodes.templating_node import TemplatingNode


class MapNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = TemplatingNode >> SearchNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
