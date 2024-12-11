from vellum.workflows import BaseWorkflow

from .nodes.final_output import FinalOutput
from .nodes.merge_node import MergeNode
from .nodes.templating_node_1 import TemplatingNode1
from .nodes.templating_node_2 import TemplatingNode2
from .nodes.templating_node_3 import TemplatingNode3


class Workflow(BaseWorkflow):
    graph = {TemplatingNode2, TemplatingNode1} >> MergeNode >> TemplatingNode3 >> FinalOutput

    class Outputs(BaseWorkflow.Outputs):
        final_output = FinalOutput.Outputs.value
