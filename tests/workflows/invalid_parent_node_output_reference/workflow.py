from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode, InlinePromptNode
from vellum.workflows.state import BaseState


class Inputs(BaseInputs):
    topic: str


class StartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        topic: str = Inputs.topic


class ReportGeneratorNode(InlinePromptNode):
    """An InlinePromptNode that defines a custom output referencing the parent class output."""

    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[JinjaPromptBlock(template="Write a report about {{ topic }}")],
        ),
    ]

    class Outputs(InlinePromptNode.Outputs):
        # BAD: These two outputs reference the parent class's output.
        # They get dropped during serialization AND they aren't resolved during execution.
        report_content: str = InlinePromptNode.Outputs.text
        report_json = InlinePromptNode.Outputs.json

        # Valid outputs
        topic: str = StartNode.Outputs.topic
        sibling_topic: str = topic
        a: str = "a"


class WorkflowWithParentOutputReference(BaseWorkflow[Inputs, BaseState]):
    graph = StartNode >> ReportGeneratorNode

    class Outputs(BaseWorkflow.Outputs):
        result = ReportGeneratorNode.Outputs.report_content
