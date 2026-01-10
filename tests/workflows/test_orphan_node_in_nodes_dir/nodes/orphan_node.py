from vellum.workflows.nodes.bases.base import BaseNode


class OrphanNodeInNodesDir(BaseNode):
    """This node is defined in the nodes/ directory but not included in graph or unused_graphs."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="orphan from nodes dir")
