from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .subworkflow_deployment import SubworkflowDeployment


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = SubworkflowDeployment.Outputs.feedback

    class Display(FinalOutputNode.Display):
        x = 800
        y = 200
