from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.ports.node_ports import NodePorts
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    value: str


class ElseWithNoIfNode(BaseNode):
    class Ports(NodePorts):
        else_branch: Port = Port.on_else()


class ElseWithNoIfWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ElseWithNoIfNode

    class Outputs(BaseOutputs):
        pass
