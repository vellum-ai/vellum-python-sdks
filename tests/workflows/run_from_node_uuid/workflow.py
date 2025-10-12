from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode


class Node1(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="node1_executed")


class Node2(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="node2_executed")


class RunFromNodeUuidWorkflow(BaseWorkflow):
    graph = Node1 >> Node2

    class Outputs(BaseWorkflow.Outputs):
        final_result = Node2.Outputs.result
