from vellum.workflows import BaseWorkflow

from .nodes.start import StartNode


class TrivialWorkflow(BaseWorkflow):
    graph = StartNode
