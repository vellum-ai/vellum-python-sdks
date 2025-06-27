from vellum.prompts.blocks import TextSystemMessage, TextUserMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable import InlinePromptNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState


class WorkflowInputs(BaseInputs):
    user_query: str


class PromptNodeWithHelpers(InlinePromptNode):
    ml_model = "gpt-4o"
    blocks = [
        TextSystemMessage("What color is the item?"),
        TextUserMessage("Here is the user query: {{user_query}}"),
    ]
    prompt_inputs = {
        "user_query": WorkflowInputs.user_query,
    }


class WorkflowWithPromptBlockHelpers(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = PromptNodeWithHelpers

    class Outputs(BaseOutputs):
        results = PromptNodeWithHelpers.Outputs.results
