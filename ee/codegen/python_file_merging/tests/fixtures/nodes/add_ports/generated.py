from vellum.workflows.nodes import BaseNode
from vellum.workflows.ports import Port

from ..inputs import Inputs


class MyCustomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    class Ports(BaseNode.Ports):
        if_branch = Port.on_if(Inputs.value.begins_with("hi"))
        another_if_branch = Port.on_if(Inputs.value.ends_with("lol"))
        else_branch = Port.on_else()

    def run(self) -> Outputs:
        return self.Outputs(value="hello")
