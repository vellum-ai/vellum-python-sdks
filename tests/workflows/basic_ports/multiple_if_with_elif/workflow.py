from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.ports.node_ports import NodePorts
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    value: str


class PassthroughNode(BaseNode):
    class Outputs(BaseOutputs):
        value = Inputs.value


class MultipleIfWithElifNode(BaseNode):
    class Ports(NodePorts):
        if_branch: Port = Port.on_if(Inputs.value.equals("foo"))
        another_if_branch: Port = Port.on_if(Inputs.value.equals("world"))
        elif_branch: Port = Port.on_elif(Inputs.value.equals("goodbye"))


class MultipleIfWithElifWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = MultipleIfWithElifNode.Ports.if_branch >> PassthroughNode

    class Outputs(BaseOutputs):
        value = PassthroughNode.Outputs.value
