from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState


class Output(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = "fdsaiofidasoj"

    class Display(FinalOutputNode.Display):
        x = 600
        y = -20
        z_index = 3
