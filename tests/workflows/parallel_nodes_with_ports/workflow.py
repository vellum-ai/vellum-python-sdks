"""
Workflow demonstrating {A, B} >> {C, D} pattern from APO-2222.

This workflow tests the serialization of a graph where:
- Two nodes (NodeA, NodeB) execute in parallel
- Both feed into NodeC which has multiple ports
- Each port leads to different downstream nodes
- The paths converge at a final node
"""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.references import LazyReference
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    value_a: str
    value_b: str


class NodeA(BaseNode):
    """First parallel node"""

    value = Inputs.value_a

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"A: {self.value}")


class NodeB(BaseNode):
    """Second parallel node"""

    value = Inputs.value_b

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"B: {self.value}")


class NodeC(BaseNode):
    """Node with multiple ports"""

    input_a = NodeA.Outputs.result
    input_b = NodeB.Outputs.result

    class Ports(BaseNode.Ports):
        path_one = Port.on_if(LazyReference(lambda: NodeC.Outputs.use_path_one))
        path_two = Port.on_else()

    class Outputs(BaseOutputs):
        combined: str
        use_path_one: bool

    def run(self) -> Outputs:
        combined = f"{self.input_a} + {self.input_b}"
        use_path_one = len(combined) > 10
        return self.Outputs(combined=combined, use_path_one=use_path_one)


class NodeD(BaseNode):
    """Node on path one"""

    value = NodeC.Outputs.combined

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"Path 1: {self.value}")


class NodeE(BaseNode):
    """Node on path two"""

    value = NodeC.Outputs.combined

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"Path 2: {self.value}")


class FinalNode(BaseNode):
    """Final convergence node"""

    from_d = NodeD.Outputs.result
    from_e = NodeE.Outputs.result

    class Outputs(BaseOutputs):
        final_result: str

    def run(self) -> Outputs:
        result = self.from_d if self.from_d else self.from_e
        return self.Outputs(final_result=result)


class ParallelNodesWithPorts(BaseWorkflow[Inputs, BaseState]):
    """
    Workflow demonstrating {A, B} >> {C, D} pattern.

    Graph structure:
        ({NodeA, NodeB} >> NodeC) >> {
            NodeC.Ports.path_one >> NodeD,
            NodeC.Ports.path_two >> NodeE
        } >> FinalNode

    Note: The pattern {A, B} >> {C.Ports.x >> D, ...} is rewritten as
    ({A, B} >> C) >> {C.Ports.x >> D, ...} because Python's set >> set
    operator is not supported. This creates a graph first, then fans out
    via ports.
    """

    graph = (
        ({NodeA, NodeB} >> NodeC)
        >> {
            NodeC.Ports.path_one >> NodeD,
            NodeC.Ports.path_two >> NodeE,
        }
        >> FinalNode
    )

    class Outputs(BaseOutputs):
        final_result = FinalNode.Outputs.final_result
