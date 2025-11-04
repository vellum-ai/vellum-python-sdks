from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.client.types.prompt_settings import PromptSettings
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class FirstNode(BaseNode):
    """A base node that outputs a string value"""

    class Outputs(BaseNode.Outputs):
        city: str

    def run(self) -> "FirstNode.Outputs":
        return self.Outputs(city="San Francisco")


class SecondNode(BaseNode):
    """Another base node that outputs a string value"""

    class Outputs(BaseNode.Outputs):
        activity: str

    def run(self) -> "SecondNode.Outputs":
        return self.Outputs(activity="hiking")


class PromptNodeWithBaseNodeInputs(BaseInlinePromptNode):
    """A prompt node that references outputs from multiple base nodes"""

    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    block_type="JINJA",
                    template="What's the best place for {{activity}} near {{city}}?",
                ),
            ],
        ),
    ]
    prompt_inputs = {
        "city": FirstNode.Outputs.city,
        "activity": SecondNode.Outputs.activity,
    }
    settings = PromptSettings(timeout=1, stream_enabled=True)


class PromptNodeWithBaseNodeInputsWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    graph = {FirstNode, SecondNode} >> PromptNodeWithBaseNodeInputs

    class Outputs(BaseOutputs):
        results = PromptNodeWithBaseNodeInputs.Outputs.results
