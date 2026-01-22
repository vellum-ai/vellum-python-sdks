from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.jinja_prompt_block import JinjaPromptBlock
from vellum.workflows.expressions.accessor import AccessorExpression
from vellum.workflows.nodes.core.templating_node.node import TemplatingNode
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.workflows.base import BaseWorkflow


class PromptNode(InlinePromptNode):
    """Prompt node that returns JSON output."""

    ml_model = "gpt-4o"
    blocks = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[JinjaPromptBlock(template="Return a JSON object with a 'response' key.")],
        )
    ]


class TemplatingNodeWithAccessorExpression(TemplatingNode):
    """
    Templating Node that incorrectly uses an accessor expression from Prompt Node JSON output.
    This pattern is not supported - users should access the JSON key within the template instead.
    """

    template = "The response is: {{ json_output }}"
    inputs = {
        "json_output": AccessorExpression(base=PromptNode.Outputs.json, field="response"),
    }


class TemplatingNodeAccessorExpressionWorkflow(BaseWorkflow):
    """Test workflow with Templating Node using accessor expression from Prompt Node JSON output."""

    graph = PromptNode >> TemplatingNodeWithAccessorExpression

    class Outputs(BaseWorkflow.Outputs):
        result = TemplatingNodeWithAccessorExpression.Outputs.result
