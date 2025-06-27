from vellum.prompts.blocks import BasicSystemMessage, BasicUserMessage
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
        BasicSystemMessage("What color is the item?"),
        BasicUserMessage("Here is the user query: {{user_query}}"),
    ]
    prompt_inputs = {
        "user_query": WorkflowInputs.user_query,
    }


class WorkflowWithPromptBlockHelpers(BaseWorkflow[WorkflowInputs, BaseState]):
    graph = PromptNodeWithHelpers

    class Outputs(BaseOutputs):
        results = PromptNodeWithHelpers.Outputs.results
