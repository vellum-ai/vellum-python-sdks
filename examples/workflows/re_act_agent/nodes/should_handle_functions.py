from vellum.workflows.nodes.displayable import ConditionalNode
from vellum.workflows.ports import Port
from vellum.workflows.references import LazyReference


class ShouldHandleFunctions(ConditionalNode):
    class Ports(ConditionalNode.Ports):
        branch_1 = Port.on_if(LazyReference("HasFunctionCalls.Outputs.result").equals("True"))
        branch_2 = Port.on_else()
