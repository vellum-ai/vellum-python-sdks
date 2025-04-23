from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.ports.node_ports import NodePorts
from vellum.workflows.ports.port import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class Inputs(BaseInputs):
    value: str


class FirstPassthroughNode(BaseNode):
    class Outputs(BaseOutputs):
        value = Inputs.value


class SecondPassthroughNode(BaseNode):
    class Outputs(BaseOutputs):
        value = Inputs.value


class MultipleInvokesNode(BaseNode):
    class Ports(NodePorts):
        if_branch: Port = Port.on_if(Inputs.value.begins_with("hi"))
        else_branch: Port = Port.on_else()
        another_if_branch: Port = Port.on_if(Inputs.value.ends_with("lol"))
        another_else_branch: Port = Port.on_else()


class MultipleInvokesWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = {
        MultipleInvokesNode.Ports.if_branch >> FirstPassthroughNode,
        MultipleInvokesNode.Ports.another_if_branch >> SecondPassthroughNode,
    }

    class Outputs(BaseOutputs):
        first_value = FirstPassthroughNode.Outputs.value
        second_value = SecondPassthroughNode.Outputs.value
