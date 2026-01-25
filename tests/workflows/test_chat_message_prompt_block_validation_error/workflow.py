from pydantic import ValidationError

from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    message: str


class ValidationErrorBlock:
    """
    A mock block that raises a Pydantic ValidationError when its block_type
    attribute is accessed during serialization.

    This simulates the Sentry error: "ValidationError: 9 validation errors for ChatMessagePromptBlock"
    """

    state = None
    cache_config = None

    @property
    def block_type(self):
        raise ValidationError.from_exception_data(
            "ChatMessagePromptBlock",
            [
                {
                    "type": "missing",
                    "loc": ("chat_role",),
                    "msg": "Field required",
                    "input": {},
                },
                {
                    "type": "missing",
                    "loc": ("blocks",),
                    "msg": "Field required",
                    "input": {},
                },
            ],
        )


chat_block = ChatMessagePromptBlock(
    chat_role="SYSTEM",
    blocks=[JinjaPromptBlock(template="Hello")],
)
object.__setattr__(chat_block, "blocks", [ValidationErrorBlock()])


class ValidationErrorPromptNode(BaseInlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [chat_block]
    prompt_inputs = {
        "message": WorkflowInputs.message,
    }


class ChatMessageValidationErrorWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = ValidationErrorPromptNode

    class Outputs(BaseOutputs):
        results = ValidationErrorPromptNode.Outputs.results
