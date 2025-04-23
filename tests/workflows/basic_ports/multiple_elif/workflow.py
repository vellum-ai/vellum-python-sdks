from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.ports.node_ports import NodePorts
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    value: str


class MultipleElifNode(BaseNode):
    class Ports(NodePorts):
        elif_branch: Port = Port.on_elif(Inputs.value.equals("foo"))
        another_elif_branch: Port = Port.on_elif(Inputs.value.equals("foo"))
        else_branch: Port = Port.on_else()


class MultipleElifWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = MultipleElifNode

    class Outputs(BaseOutputs):
        pass
