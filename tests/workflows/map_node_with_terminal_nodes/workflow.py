from typing import List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    items: List[str]


class MapIterationNode(BaseNode):
    """Node inside the map subworkflow"""

    item = MapNode.SubworkflowInputs.item

    class Outputs(BaseOutputs):
        processed: str

    def run(self) -> Outputs:
        return self.Outputs(processed=self.item)


class MapSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = MapIterationNode

    class Outputs(BaseOutputs):
        processed: str = MapIterationNode.Outputs.processed


class MyMapNode(MapNode):
    items = Inputs.items
    subworkflow = MapSubworkflow


class TopLevelTerminalNode(FinalOutputNode):
    """Terminal node at the top level"""

    class Outputs(FinalOutputNode.Outputs):
        value = MyMapNode.Outputs.processed


class MapNodeWithTerminalNodes(BaseWorkflow[Inputs, BaseState]):
    graph = MyMapNode >> TopLevelTerminalNode

    class Outputs(BaseOutputs):
        final_result = TopLevelTerminalNode.Outputs.value
