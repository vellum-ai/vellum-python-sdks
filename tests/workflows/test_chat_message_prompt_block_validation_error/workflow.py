from vellum import ChatMessagePromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    message: str


class InvalidBlockType:
    """A mock object with an invalid block_type that will trigger a ValidationError during serialization."""

    block_type = "INVALID_BLOCK_TYPE"
    state = None
    cache_config = None


class ValidationErrorPromptNode(BaseInlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="SYSTEM",
            blocks=[InvalidBlockType()],  # type: ignore[list-item]
        )
    ]
    prompt_inputs = {
        "message": WorkflowInputs.message,
    }


class ChatMessageValidationErrorWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = ValidationErrorPromptNode

    class Outputs(BaseOutputs):
        results = ValidationErrorPromptNode.Outputs.results
