from vellum.workflows import BaseNode


class MySubworkflowNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    class Display(BaseNode.Display):
        icon = "vellum:icon:square"
        color = "peach"
