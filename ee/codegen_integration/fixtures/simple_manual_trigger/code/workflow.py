from vellum.workflows import BaseWorkflow
from vellum.workflows.triggers.manual import ManualTrigger

from .nodes.final_output import FinalOutput
from .nodes.simple_node import SimpleNode


class Workflow(BaseWorkflow):
    graph = ManualTrigger >> SimpleNode >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
