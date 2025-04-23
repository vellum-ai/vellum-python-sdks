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


class IfElifElseNode(BaseNode):
    class Ports(NodePorts):
        if_branch: Port = Port.on_if(Inputs.value.equals("foo"))
        elif_branch: Port = Port.on_elif(Inputs.value.equals("foo"))
        else_branch: Port = Port.on_else()


class IfElifElseWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = IfElifElseNode.Ports.if_branch >> PassthroughNode

    class Outputs(BaseOutputs):
        value = PassthroughNode.Outputs.value
