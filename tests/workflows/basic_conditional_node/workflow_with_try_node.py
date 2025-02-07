from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode, ConditionalNode, TryNode
from vellum.workflows.ports import Port
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    name: str


@TryNode.wrap()
class Node(BaseNode):
    class Outputs(BaseNode.Outputs):
        text_str = Inputs.name


class MiddleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        text_str = "fail"


class MiddleNode2(BaseNode):
    class Outputs(BaseNode.Outputs):
        text_str = "pass"


class FinalNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value = MiddleNode2.Outputs.text_str


class ConditionalNode(ConditionalNode):
    class Ports(ConditionalNode.Ports):
        branch_1 = Port.on_if(Node.Outputs.error.contains("Provider Error"))
        branch_2 = Port.on_else()


class Workflow(BaseWorkflow[Inputs, BaseState]):
    graph = {
        Node
        >> {ConditionalNode.Ports.branch_1 >> MiddleNode, ConditionalNode.Ports.branch_2 >> MiddleNode2 >> FinalNode}
    }

    class Outputs(BaseWorkflow.Outputs):
        pass_final_output = FinalNode.Outputs.value
        fail_final_output = MiddleNode.Outputs.text_str
