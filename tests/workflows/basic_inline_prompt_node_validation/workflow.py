from vellum import ChatMessagePromptBlock, VariablePromptBlock
from vellum.client.types.prompt_settings import PromptSettings
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    noun: str


class ExampleBaseInlinePromptNode(BaseInlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[
                VariablePromptBlock(input_variable="noun"),
            ],
        ),
    ]
    prompt_inputs = {}  # No prompt inputs are provided
    settings = PromptSettings(timeout=1)


class BasicInlinePromptWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = ExampleBaseInlinePromptNode

    class Outputs(BaseOutputs):
        results = ExampleBaseInlinePromptNode.Outputs.results
