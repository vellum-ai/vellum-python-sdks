from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable.bases.inline_prompt_node import BaseInlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    message: str


class InvalidBlockType:
    """A mock object with an invalid block_type that will trigger serialization error."""

    block_type = "INVALID_BLOCK_TYPE"
    state = None
    cache_config = None


# Create a ChatMessagePromptBlock with an invalid child block
# The child block has an invalid block_type that is not supported
chat_block = ChatMessagePromptBlock(
    chat_role="SYSTEM",
    blocks=[JinjaPromptBlock(template="Hello")],
)
# Replace the valid blocks with an invalid one using object.__setattr__
# to bypass Pydantic's frozen model validation
object.__setattr__(chat_block, "blocks", [InvalidBlockType()])


class InvalidChildPromptNode(BaseInlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [chat_block]
    prompt_inputs = {
        "message": WorkflowInputs.message,
    }


class InvalidChatMessageChildWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = InvalidChildPromptNode

    class Outputs(BaseOutputs):
        results = InvalidChildPromptNode.Outputs.results
