from vellum.workflows.nodes.displayable import ConditionalNode
from vellum.workflows.ports import Port
from vellum.workflows.references import LazyReference

from .problem_solver_agent import ProblemSolverAgent


class NeedsRevision(ConditionalNode):
    """Here we retry up to 3 times until the status is acceptable, or we give up. You can use the scrubber at the bottom of the page to see the results on each loop."""

    class Ports(ConditionalNode.Ports):
        branch_1 = Port.on_if(LazyReference("ExtractStatus.Outputs.result").equals("acceptable"))
        branch_2 = Port.on_elif(ProblemSolverAgent.Execution.count.less_than(4))
        branch_3 = Port.on_else()
