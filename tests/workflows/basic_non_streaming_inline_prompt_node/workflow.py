from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.client.types.prompt_settings import PromptSettings
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    noun: str


class ExampleNonStreamingInlinePromptNode(BaseInlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                JinjaPromptBlock(
                    block_type="JINJA",
                    template="What's your favorite {{noun}}?",
                ),
            ],
        ),
    ]
    prompt_inputs = {
        "noun": WorkflowInputs.noun,
    }
    settings = PromptSettings(stream_enabled=False)


class BasicNonStreamingInlinePromptWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = ExampleNonStreamingInlinePromptNode

    class Outputs(BaseOutputs):
        results = ExampleNonStreamingInlinePromptNode.Outputs.results
