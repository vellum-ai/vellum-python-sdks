from vellum.workflows.nodes.bases import BaseNode


class Node2(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="node2_executed")
