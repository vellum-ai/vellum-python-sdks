from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    topic: str


class ReportGeneratorNode(InlinePromptNode):
    """An InlinePromptNode that defines a custom output referencing the parent class output."""

    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[JinjaPromptBlock(template="Write a report about {{ topic }}")],
        ),
    ]
    prompt_inputs = {"topic": Inputs.topic}

    class Outputs(InlinePromptNode.Outputs):
        # BAD: This references the parent class's output.
        # It gets dropped during serialization AND it isn't resolved during execution.
        report_content: str = InlinePromptNode.Outputs.text
        report_json = InlinePromptNode.Outputs.json
        a: str = "a"


class WorkflowWithParentOutputReference(BaseWorkflow[Inputs, BaseState]):
    graph = ReportGeneratorNode

    class Outputs(BaseWorkflow.Outputs):
        result = ReportGeneratorNode.Outputs.report_content
