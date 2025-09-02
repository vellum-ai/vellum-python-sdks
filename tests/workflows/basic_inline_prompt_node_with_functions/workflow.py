from vellum import ChatMessagePromptBlock, FunctionDefinition, JinjaPromptBlock
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    noun: str


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
        "noun": WorkflowInputs.noun,
    }
    functions = [
        FunctionDefinition(
            name="favorite_noun",
            description="Returns the favorite noun of the user",
            parameters={},
        ),
    ]


class BasicInlinePromptWithFunctionsWorkflow(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = ExampleBaseInlinePromptNodeWithFunctions

    class Outputs(BaseWorkflow.Outputs):
        results = ExampleBaseInlinePromptNodeWithFunctions.Outputs.results
