from vellum.workflows import BaseWorkflow

from .nodes import Node1, Node2


class RunFromNodeUuidWorkflow(BaseWorkflow):
    graph = Node1 >> Node2

    class Outputs(BaseWorkflow.Outputs):
        final_result = Node2.Outputs.result
