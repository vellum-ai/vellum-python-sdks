from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class StartNode(BaseNode):
    pass


class TrivialWorkflow(BaseWorkflow):
    graph = StartNode
