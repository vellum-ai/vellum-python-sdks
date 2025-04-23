from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.ports import NodePorts, Port
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    value: str


class PassthroughNode(BaseNode):
    class Outputs(BaseOutputs):
        value = Inputs.value


class AnotherPassthroughNode(BaseNode):
    class Outputs(BaseOutputs):
        value = Inputs.value


class MultipleIfElifElseNode(BaseNode):
    class Ports(NodePorts):
        if_branch: Port = Port.on_if(Inputs.value.equals("foo"))
        elif_branch: Port = Port.on_elif(Inputs.value.equals("foo"))
        else_branch: Port = Port.on_else()
        another_if_branch: Port = Port.on_if(Inputs.value.equals("foo"))
        another_elif_branch: Port = Port.on_elif(Inputs.value.equals("foo"))
        another_else_branch: Port = Port.on_else()


class MultipleIfElifElseWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = {
        MultipleIfElifElseNode.Ports.if_branch >> PassthroughNode,
        MultipleIfElifElseNode.Ports.another_if_branch >> AnotherPassthroughNode,
    }

    class Outputs(BaseOutputs):
        value = PassthroughNode.Outputs.value
        another_value = AnotherPassthroughNode.Outputs.value
