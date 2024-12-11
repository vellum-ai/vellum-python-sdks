from vellum.workflows import BaseWorkflow

from .nodes.final_output import FinalOutput
from .nodes.search_node import SearchNode


class SubworkflowNodeWorkflow(BaseWorkflow):
    graph = SearchNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
