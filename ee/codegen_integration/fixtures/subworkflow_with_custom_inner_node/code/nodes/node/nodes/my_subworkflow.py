from vellum.workflows import BaseNode


class MySubworkflowNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    class Display(BaseNode.Display):
        x = 0
        y = 0
        icon = "vellum:icon:square"
        color = "peach"
