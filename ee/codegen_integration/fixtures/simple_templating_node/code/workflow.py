from vellum.workflows import BaseWorkflow

from .nodes.final_output import FinalOutput
from .nodes.templating_node import TemplatingNode


class Workflow(BaseWorkflow):
    graph = TemplatingNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
