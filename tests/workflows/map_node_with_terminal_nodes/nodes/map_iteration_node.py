from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs


class MapIterationNode(BaseNode):
    """Node inside the map subworkflow"""

    item = MapNode.SubworkflowInputs.item

    class Outputs(BaseOutputs):
        processed: str

    def run(self) -> Outputs:
        return self.Outputs(processed=self.item)
