from vellum.workflows.nodes.displayable import ConditionalNode
from vellum.workflows.ports import Port

from .extract_score import ExtractScore


class AdvanceOrReject(ConditionalNode):
    class Ports(ConditionalNode.Ports):
        branch_1 = Port.on_if(ExtractScore.Outputs.result.equals("Advance"))
        branch_2 = Port.on_else()
