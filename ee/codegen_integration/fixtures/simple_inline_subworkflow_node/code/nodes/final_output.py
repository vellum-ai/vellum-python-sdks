from vellum.workflows.nodes.displayable import FinalOutputNode

from .subworkflow_node import SubworkflowNode


class FinalOutput(FinalOutputNode[str]):
    class Outputs(FinalOutputNode.Outputs):
        value = SubworkflowNode.Outputs.final_output
