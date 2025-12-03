from vellum.workflows import BaseWorkflow

from .nodes.output import Output
from .triggers.scheduled import Scheduled


class Workflow(BaseWorkflow):
    graph = {
        Output,
        Scheduled >> Output,
    }

    class Outputs(BaseWorkflow.Outputs):
        output = Output.Outputs.value
