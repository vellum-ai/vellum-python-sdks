from vellum.workflows.nodes.displayable import ConditionalNode
from vellum.workflows.ports import Port
from vellum.workflows.references import LazyReference


class ConditionalNode10(ConditionalNode):
    class Ports(ConditionalNode.Ports):
        branch_1 = Port.on_if(LazyReference("OutputType.Outputs.result").equals("FUNCTION_CALL"))
        branch_2 = Port.on_else()
