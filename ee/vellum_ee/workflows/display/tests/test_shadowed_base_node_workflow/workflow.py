from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlineSubworkflowNode
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


# A custom base node class with the same name as the subworkflow class
class NestedWorkflow(BaseNode):
    """A custom base node with the same name as the subworkflow class."""

    class Outputs(BaseOutputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="base_result")


# A node that extends the custom base node
class MyNode(NestedWorkflow):
    """A node that extends the NestedWorkflow base node."""

    def run(self) -> NestedWorkflow.Outputs:
        return self.Outputs(result="result")


# The actual subworkflow class - same name as the base node class above
# This redefines NestedWorkflow, shadowing the base node class
class NestedWorkflow(BaseWorkflow[BaseInputs, BaseState]):  # type: ignore[no-redef]
    """The actual subworkflow with the same name as the base node class."""

    graph = MyNode

    class Outputs(BaseOutputs):
        result = MyNode.Outputs.result


class ExampleInlineSubworkflowNode(InlineSubworkflowNode):
    subworkflow_inputs = {}
    subworkflow = NestedWorkflow  # type: ignore[assignment]


class ShadowedBaseNodeWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    graph = ExampleInlineSubworkflowNode

    class Outputs(BaseOutputs):
        result = ExampleInlineSubworkflowNode.Outputs.result
