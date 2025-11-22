from vellum.workflows import BaseWorkflow

from .nodes.the_end import TheEnd


class Workflow(BaseWorkflow):
    graph = TheEnd

    class Outputs(BaseWorkflow.Outputs):
        the_end = TheEnd.Outputs.value
