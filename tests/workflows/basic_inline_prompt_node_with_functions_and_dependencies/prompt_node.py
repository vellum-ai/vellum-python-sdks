from vellum import ChatMessagePromptBlock, JinjaPromptBlock
from vellum.workflows.nodes import InlinePromptNode, TryNode
from vellum.workflows.references import LazyReference

from tests.workflows.basic_inline_prompt_node_with_functions_and_dependencies.inputs import WorkflowInputs


@TryNode.wrap()
class ExampleBaseInlinePromptNodeWithFunctions(InlinePromptNode):
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
        "noun": LazyReference("StartNode.Outputs.final_noun").coalesce(WorkflowInputs.noun),
    }
