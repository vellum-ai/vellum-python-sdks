from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.client.types.prompt_settings import PromptSettings
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.nodes.core.retry_node import RetryNode
from vellum.workflows.nodes.displayable import GuardrailNode
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    noun: str


@RetryNode.wrap(max_attempts=3)
class RetryablePromptNode(InlinePromptNode):
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
    settings = PromptSettings(timeout=1, stream_enabled=True)


class ConsumerGuardrailNode(GuardrailNode):
    metric_definition = "e0869d84-1bb6-4e8c-85ad-67fd28ff8f59"
    metric_inputs = {
        "actual": RetryablePromptNode.Outputs.text,
    }
    release_tag = "LATEST"


class WorkflowWithRetryAndGuardrailNodes(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = RetryablePromptNode >> ConsumerGuardrailNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = ConsumerGuardrailNode.Outputs.score
