"""
Workflow for APO-1936: Conditional nodes internal server error when doing string greater than or equal comparisons.

This workflow reproduces the error by creating a conditional node with ports that use
comparison expressions on string values.
"""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.ports.port import Port
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    field: str
    value: float


class ConditionalNode(BaseNode):
    class Ports(BaseNode.Ports):
        if_port = Port.on_if(Inputs.field.greater_than_or_equal_to(Inputs.value))
        else_port = Port.on_else()

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="if_branch")


class ElseNode(BaseNode):
    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="else_branch")


class StringComparisonErrorWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ConditionalNode.Ports.else_port >> ElseNode

    class Outputs(BaseOutputs):
        final_result = ConditionalNode.Outputs.result.coalesce(ElseNode.Outputs.result)
