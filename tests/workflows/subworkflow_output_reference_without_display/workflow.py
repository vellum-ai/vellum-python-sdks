from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode, InlineSubworkflowNode
from vellum.workflows.outputs.base import BaseOutputs

from tests.workflows.subworkflow_output_reference_without_display.child_workflow import ChildWorkflow


class SubworkflowNodeExample(InlineSubworkflowNode):
    subworkflow = ChildWorkflow


class FollowOnNode(BaseNode):
    input_value = SubworkflowNodeExample.Outputs.result

    class Outputs(BaseOutputs):
        final: int

    def run(self) -> Outputs:
        return self.Outputs(final=self.input_value)


class SubworkflowOutputReferenceWorkflow(BaseWorkflow):
    graph = SubworkflowNodeExample >> FollowOnNode

    class Outputs(BaseOutputs):
        final_result = FollowOnNode.Outputs.final
