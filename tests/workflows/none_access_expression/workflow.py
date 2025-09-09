from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable import FinalOutputNode, InlinePromptNode
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.state import BaseState


class PromptNode(InlinePromptNode):
    ml_model = "gpt-4o-mini"
    blocks = []


class Output(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = ConstantValueReference(None)["message"]


class Workflow(BaseWorkflow):
    graph = PromptNode >> Output

    class Outputs(BaseWorkflow.Outputs):
        output = Output.Outputs.value
