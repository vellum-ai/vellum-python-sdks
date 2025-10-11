from vellum.workflows.nodes.bases import BaseNode


class Node1(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="node1_executed")
