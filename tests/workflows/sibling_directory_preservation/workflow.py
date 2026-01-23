from vellum.workflows import BaseWorkflow

from .nodes.start import StartNode


class SiblingDirectoryPreservationWorkflow(BaseWorkflow):
    graph = StartNode
