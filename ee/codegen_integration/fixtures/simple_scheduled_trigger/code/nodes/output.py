from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState


class Output(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = "fdsaiofidasoj"

    class Display(FinalOutputNode.Display):
        icon = "vellum:icon:circle-stop"
        color = "teal"
