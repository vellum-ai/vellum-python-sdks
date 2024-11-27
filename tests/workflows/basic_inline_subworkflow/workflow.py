from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlineSubworkflowNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState


class Inputs(BaseInputs):
    city: str
    date: str


class NestedInputs(BaseInputs):
    metro: str


class StartNode(BaseNode):
    metro = NestedInputs.metro
    date = Inputs.date

    class Outputs(BaseOutputs):
        temperature: float
        reasoning: str

    def run(self) -> Outputs:
        return self.Outputs(temperature=70, reasoning=f"The weather in {self.metro} on {self.date} was hot")


class NestedWorkflow(BaseWorkflow[NestedInputs, BaseState]):
    graph = StartNode

    class Outputs(BaseOutputs):
        temperature = StartNode.Outputs.temperature
        reasoning = StartNode.Outputs.reasoning


class ExampleInlineSubworkflowNode(InlineSubworkflowNode):
    subworkflow_inputs = {
        "metro": Inputs.city,
    }
    subworkflow = NestedWorkflow

    class Outputs(InlineSubworkflowNode.Outputs):
        temperature = NestedWorkflow.Outputs.temperature
        reasoning = NestedWorkflow.Outputs.reasoning


class BasicInlineSubworkflowWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = ExampleInlineSubworkflowNode

    class Outputs(BaseOutputs):
        temperature = ExampleInlineSubworkflowNode.Outputs.temperature
        reasoning = ExampleInlineSubworkflowNode.Outputs.reasoning
